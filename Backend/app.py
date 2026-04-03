from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import shutil
import time
import threading
from werkzeug.utils import secure_filename
from utils.novel_processor import NovelProcessor
from utils.graph_generator import GraphGenerator
from utils.centrality_calculator import CentralityCalculator
from utils.faction_analyzer import FactionAnalyzer
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

processed_data = {
    'novel_content': None,
    'chapters': [],
    'characters': {},
    'main_characters': [],
    'current_graph': None,
    'paragraphs_info': [],
    'temp_file_path': None,
    'upload_time': None
}

processor = NovelProcessor()
graph_generator = GraphGenerator()
centrality_calc = CentralityCalculator()
faction_analyzer = FactionAnalyzer(threshold=1, use_louvain=True)


def cleanup_temp_files():
    """清理过期的临时文件"""
    try:
        current_time = time.time()
        lifetime = Config.TEMP_FILE_LIFETIME

        if os.path.exists(Config.UPLOAD_FOLDER):
            for filename in os.listdir(Config.UPLOAD_FOLDER):
                file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                try:
                    file_mtime = os.path.getmtime(file_path)
                    if current_time - file_mtime > lifetime:
                        os.remove(file_path)
                        print(f"已清理过期临时文件：{filename}")
                except Exception as e:
                    print(f"清理文件失败 {filename}: {e}")
    except Exception as e:
        print(f"清理临时文件失败：{e}")


def periodic_cleanup():
    """定期清理临时文件（每 30 分钟运行一次）"""
    while True:
        time.sleep(1800)  # 30 分钟
        cleanup_temp_files()


# 启动后台清理线程
cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
cleanup_thread.start()

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式，仅支持 txt 和 pdf'}), 400

    # 使用临时文件而不是永久存储
    import tempfile
    temp_fd, filepath = tempfile.mkstemp(suffix='.' + file.filename.rsplit('.', 1)[1].lower())

    try:
        file.save(filepath)

        result = processor.process_novel(filepath)

        if not result['content'] or len(result['content'].strip()) == 0:
            return jsonify({
                'error': '无法从文件中提取有效文本内容，请检查文件是否为纯图片 PDF'
            }), 400

        processed_data['novel_content'] = result['content']
        processed_data['chapters'] = result['chapters']
        processed_data['characters'] = result['characters']
        processed_data['paragraphs_info'] = result['paragraphs_info']

        main_chars = centrality_calc.calculate_main_characters(
            result['characters'],
            result['paragraphs_info'],
            top_n=10
        )
        processed_data['main_characters'] = main_chars

        if len(result['chapters']) > 0:
            first_chapter_idx = result['chapter_indices'][0]
            graph_data = graph_generator.generate_chapter_graph(
                result['content'],
                first_chapter_idx,
                result['paragraphs_info']
            )

            faction_colors = faction_analyzer.analyze_factions(graph_data)
            graph_data_with_colors = graph_generator.apply_faction_colors(graph_data, faction_colors)

            processed_data['current_graph'] = graph_data_with_colors

            return jsonify({
                'success': True,
                'message': '文件处理成功',
                'total_chapters': len(result['chapters']),
                'chapter_titles': [ch['title'] for ch in result['chapters']],
                'main_characters': main_chars,
                'graph_data': graph_data_with_colors
            })
        else:
            return jsonify({'error': '未找到章节'}), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'处理失败：{str(e)}'}), 500

    finally:
        # 处理完成后删除临时文件
        try:
            os.close(temp_fd)
            os.unlink(filepath)
        except:
            pass


@app.route('/api/chapter/<int:chapter_idx>', methods=['GET'])
def get_chapter_graph(chapter_idx):
    """获取指定章节的人物关系图谱"""
    if processed_data['novel_content'] is None:
        return jsonify({'error': '请先上传文件'}), 400

    try:
        # 重新生成该章节的图谱
        graph_data = graph_generator.generate_chapter_graph(
            processed_data['novel_content'],
            chapter_idx,
            processed_data['paragraphs_info']
        )

        # 阵营分析并为连线着色
        faction_colors = faction_analyzer.analyze_factions(graph_data)
        graph_data_with_colors = graph_generator.apply_faction_colors(graph_data, faction_colors)

        processed_data['current_graph'] = graph_data_with_colors

        return jsonify({
            'success': True,
            'graph_data': graph_data_with_colors
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取章节图谱失败：{str(e)}'}), 500

@app.route('/api/character/<character_name>', methods=['GET'])
def get_character_quotes(character_name):
    """获取指定人物在当前章节的相关语句"""
    if processed_data['current_graph'] is None:
        return jsonify({'error': '请先选择章节'}), 400

    try:
        chapter_idx = processed_data['current_graph'].get('chapter_index', 0)

        # 查找该人物在章节中的相关语句
        quotes = processor.find_character_quotes(
            processed_data['novel_content'],
            character_name,
            chapter_idx,
            processed_data['paragraphs_info']
        )

        return jsonify({
            'success': True,
            'character_name': character_name,
            'quotes': quotes
        })

    except Exception as e:
        return jsonify({'error': f'获取语录失败：{str(e)}'}), 500

@app.route('/api/main-characters', methods=['GET'])
def get_main_characters():
    """获取主角列表（度中心性最高的角色）"""
    if processed_data['main_characters'] is None:
        return jsonify({'error': '请先上传文件'}), 400

    return jsonify({
        'success': True,
        'main_characters': processed_data['main_characters']
    })

@app.route('/api/custom-dict', methods=['GET'])
def get_custom_dict():
    """获取自定义词典中的人物列表"""
    try:
        names = NovelProcessor.get_custom_dict()
        return jsonify({
            'success': True,
            'names': names
        })
    except Exception as e:
        return jsonify({'error': f'获取自定义词典失败：{str(e)}'}), 500

@app.route('/api/custom-dict', methods=['POST'])
def add_to_custom_dict():
    """添加人物到自定义词典"""
    if 'names' not in request.json:
        return jsonify({'error': '缺少 names 参数'}), 400

    names = request.json['names']
    if not isinstance(names, list):
        return jsonify({'error': 'names 必须是列表'}), 400

    try:
        # 添加到内存中的词典
        NovelProcessor.add_to_custom_dict(names)

        # 保存到文件
        NovelProcessor.save_custom_dict(names)

        return jsonify({
            'success': True,
            'message': f'成功添加 {len(names)} 个人物'
        })
    except Exception as e:
        return jsonify({'error': f'添加自定义词典失败：{str(e)}'}), 500

@app.route('/api/custom-dict', methods=['DELETE'])
def remove_from_custom_dict():
    """从自定义词典中删除人物"""
    if 'names' not in request.json:
        return jsonify({'error': '缺少 names 参数'}), 400

    names = request.json['names']
    if not isinstance(names, list):
        return jsonify({'error': 'names 必须是列表'}), 400

    try:
        NovelProcessor.remove_from_custom_dict(names)

        return jsonify({
            'success': True,
            'message': f'成功删除 {len(names)} 个人物'
        })
    except Exception as e:
        return jsonify({'error': f'删除自定义词典失败：{str(e)}'}), 500

@app.route('/api/cleanup', methods=['POST'])
def cleanup():
    """手动触发清理临时文件"""
    try:
        cleanup_temp_files()
        return jsonify({
            'success': True,
            'message': '临时文件清理完成'
        })
    except Exception as e:
        return jsonify({'error': f'清理失败：{str(e)}'}), 500

def allowed_file(filename):
    """检查文件类型是否允许"""
    allowed_extensions = {'txt', 'pdf'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

# 应用启动时清理一次过期文件
cleanup_temp_files()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

