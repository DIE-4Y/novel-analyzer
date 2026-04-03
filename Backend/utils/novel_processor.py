import os
import re
from tqdm import tqdm
from pyhanlp import *
from Backend.config import Config

class NovelProcessor:
    def __init__(self, analyzer_type="Perceptron", custom_dict=True):
        """初始化 HanLP 分析器"""
        data_path = "C:/Users/faker/AppData/Local/Programs/Python/Python312/Lib/site-packages/pyhanlp/static/data/model/perceptron/large/cws.bin"

        self.CRFLAnalyzer = JClass("com.hankcs.hanlp.model.crf.CRFLexicalAnalyzer")()

        PLAnalyzer = JClass("com.hankcs.hanlp.model.perceptron.PerceptronLexicalAnalyzer")
        self.PLAnalyzer = PLAnalyzer(
            data_path,
            HanLP.Config.PerceptronPOSModelPath,
            HanLP.Config.PerceptronNERModelPath
        )

        self.analyzer = self.PLAnalyzer
        if analyzer_type == "Perceptron":
            self.analyzer = self.PLAnalyzer.enableCustomDictionary(custom_dict)
        elif analyzer_type == "CRF":
            self.analyzer = self.CRFLAnalyzer.enableCustomDictionary(custom_dict)

        self.paragraphs_info = []

        # 加载自定义词典
        self._load_custom_dictionary()

    def _load_custom_dictionary(self):
        """加载自定义词典文件"""
        try:
            if os.path.exists(Config.CUSTOM_DICT_FILE):
                with open(Config.CUSTOM_DICT_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        name = line.strip()
                        if name and len(name) > 0:
                            CustomDictionary.add(name, "nr 1000 ")
        except Exception as e:
            print(f"加载自定义词典失败：{e}")

    @staticmethod
    def add_to_custom_dict(names):
        """
        静态方法：添加人物到自定义词典

        Args:
            names: 人物名称列表
        """
        for name in names:
            name = name.strip()
            if name:
                if CustomDictionary.get(name) is None:
                    CustomDictionary.add(name, "nr 1000 ")
                else:
                    attr = "nr 1000 " + str(CustomDictionary.get(name))
                    CustomDictionary.insert(name, attr)

    @staticmethod
    def save_custom_dict(names):
        """
        静态方法：保存自定义词典到文件

        Args:
            names: 人物名称列表
        """
        try:
            existing_names = set()
            if os.path.exists(Config.CUSTOM_DICT_FILE):
                with open(Config.CUSTOM_DICT_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        existing_names.add(line.strip())

            all_names = existing_names | set(name.strip() for name in names if name.strip())

            with open(Config.CUSTOM_DICT_FILE, 'w', encoding='utf-8') as f:
                for name in sorted(all_names):
                    if name:
                        f.write(name + '\n')

            return True
        except Exception as e:
            print(f"保存自定义词典失败：{e}")
            return False

    @staticmethod
    def get_custom_dict():
        """
        静态方法：获取自定义词典中的所有人物

        Returns:
            人物名称列表
        """
        try:
            if os.path.exists(Config.CUSTOM_DICT_FILE):
                with open(Config.CUSTOM_DICT_FILE, 'r', encoding='utf-8') as f:
                    return [line.strip() for line in f if line.strip()]
            return []
        except Exception as e:
            print(f"读取自定义词典失败：{e}")
            return []

    @staticmethod
    def remove_from_custom_dict(names):
        """
        静态方法：从自定义词典中删除人物

        Args:
            names: 人物名称列表
        """
        try:
            existing_names = set()
            if os.path.exists(Config.CUSTOM_DICT_FILE):
                with open(Config.CUSTOM_DICT_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        existing_names.add(line.strip())

            new_names = existing_names - set(name.strip() for name in names if name.strip())

            with open(Config.CUSTOM_DICT_FILE, 'w', encoding='utf-8') as f:
                for name in sorted(new_names):
                    if name:
                        f.write(name + '\n')

            return True
        except Exception as e:
            print(f"删除自定义词典失败：{e}")
            return False

    def add_characters_to_dict(self, names_list):
        """添加人物到自定义词典"""
        for n in names_list:
            if CustomDictionary.get(n) is None:
                CustomDictionary.add(n, "nr 1000 ")
            else:
                attr = "nr 1000 " + str(CustomDictionary.get(n))
                CustomDictionary.insert(n, attr)

    def cut_text(self, text):
        """使用 HanLP 分词并识别人名"""
        terms = self.analyzer.seg(text)
        result = []
        for term in terms:
            result.append((str(term.word), str(term.nature)))
        return result

    def process_novel(self, filepath):
        """处理小说文件，提取人物和章节信息"""
        content = self._read_file(filepath)

        characters_initial = self._extract_characters(content)

        high_freq_chars = [name for name, count in characters_initial.items() if count >= 5]
        if high_freq_chars:
            self.add_characters_to_dict(high_freq_chars)

        characters = self._extract_characters(content)

        chapters = self._split_chapters(content)

        self.paragraphs_info = self._analyze_paragraphs(content, chapters)

        return {
            'content': content,
            'chapters': chapters,
            'characters': characters,
            'chapter_indices': [ch['index'] for ch in chapters],
            'paragraphs_info': self.paragraphs_info
        }

    def _read_file(self, filepath):
        """读取文件内容，支持 txt 和 pdf 格式"""
        file_ext = filepath.rsplit('.', 1)[1].lower()

        if file_ext == 'txt':
            return self._read_txt_file(filepath)
        elif file_ext == 'pdf':
            return self._read_pdf_file(filepath)
        else:
            raise ValueError(f'不支持的文件格式：{file_ext}')

    def _read_txt_file(self, filepath):
        """读取 TXT 文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='gbk') as f:
                return f.read()

    def _read_pdf_file(self, filepath):
        """读取 PDF 文件，保留自然段结构"""
        try:
            import fitz

            doc = fitz.open(filepath)

            all_pages_text = []
            found_text = False

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")

                if text and text.strip():
                    found_text = True
                    cleaned_text = text.strip()
                    all_pages_text.append(cleaned_text)

            doc.close()

            if not found_text:
                return ""

            full_text = "\n".join(all_pages_text)

            full_text = re.sub(r'\n{3,}', '\n\n', full_text)

            return full_text

        except ImportError:
            raise ImportError("需要安装 PyMuPDF 库：pip install PyMuPDF")
        except Exception as e:
            raise Exception(f"PDF 读取失败：{str(e)}")

    def _is_valid_character_name(self, name):
        """
        判断是否是有效的人名（增强版）

        Args:
            name: 待判断的名称

        Returns:
            bool: 是否为有效人名
        """
        # 1. 长度检查：排除长度小于 2 的字符
        if len(name) < 2 or len(name) > 5:
            return False

        # 2. 排除纯标点符号
        if re.match(r'^[\W_]+$', name):
            return False

        # 3. 排除常见标点符号组合
        invalid_patterns = [
            r'^[.,!?;:,.!?.]*$',
            r'^[""\']+$',
            r'^[()（）]+$',
            r'^[……—～`·]+$',
        ]
        for pattern in invalid_patterns:
            if re.match(pattern, name):
                return False

        # 4. 排除常见语气词和助词
        invalid_words = {
            '了', '的', '吗', '呢', '吧', '啊', '呀', '哦', '嗯', '哎',
            '嘛', '啦', '呗', '咯', '哈', '嘿', '哇', '噻', '嘟', '呐'
        }
        if name in invalid_words:
            return False

        # 5. 排除常见代词和称谓（非人名）
        invalid_pronouns = {
            '我', '你', '他', '她', '它', '咱', '您', '这', '那',
            '谁', '啥', '何', '某', '其', '此', '彼'
        }
        if name in invalid_pronouns:
            return False

        # 6. 排除数字或字母开头的
        if re.match(r'^[0-9a-zA-Z]', name):
            return False

        # 7. 排除包含非中文字符的（除非是少数民族名字）
        if not re.match(r'^[\u4e00-\u9fa5]+([·][\u4e00-\u9fa5]+)*$', name):
            return False

        # 8. 排除重复字符（如"啊啊啊"、"哈哈哈"）
        if len(set(name)) == 1 and len(name) > 1:
            return False

        # 9. 【新增】排除明显非人名的噪声词
        noise_words = {
            # 泛指类
            '某人', '有人', '众人', '人人', '人人', '人们', '人家',
            '群众', '百姓', '民众', '平民', '凡人', '俗人',
            '大家', '各位', '诸位', '列位', '各位',
            '他们', '她们', '它们', '咱们', '我们', '你们',

            # 身份类（非具体人名）
            '路人', '行人', '旁人', '他人', '外人', '生人',
            '看客', '观众', '听众', '读者', '作者',
            '角色', '人物', '主角', '配角', '反派',

            # 称呼类（非具体人名）
            '大人', '小人', '官人', '老爷', '少爷', '小姐',
            '夫人', '太太', '奶奶', '姥姥', '爷爷',
            '师父', '师傅', '徒弟', '弟子', '门人',
            '长老', '前辈', '后辈', '高人', '奇人',
            '神仙', '仙人', '妖怪', '魔鬼', '鬼怪',

            # 其他噪声
            '无名', '无名氏', '佚名', '未知', '神秘人',
            '一个人', '一个人影', '一道声音', '一个声音',
            '一个老者', '一个中年', '一个青年', '一个少年',
            '一个女子', '一个男子', '一个女人', '一个男人',
            '一位', '这名', '那位', '这个', '那个',
        }

        if name in noise_words:
            return False

        # 10. 排除包含"人"字但不是人名的词
        if '人' in name and len(name) == 2:
            # 特殊情况：允许"某人"这种已经被上面排除的，但防止漏网
            if name != '某人' and name.endswith('人'):
                return False

        return True

    def _extract_characters(self, content):
        """提取全文人物并统计出现次数（带过滤）"""
        characters = {}

        paragraphs = content.split('\n')

        for paragraph in tqdm(paragraphs, desc="Extracting characters"):
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            words = self.cut_text(paragraph)

            for word, flag in words:
                if flag in ['nr', 'nrf']:
                    if self._is_valid_character_name(word):
                        characters[word] = characters.get(word, 0) + 1

        return characters

    def _split_chapters(sell, content):
        """
        将小说内容按章节划分，返回章节列表。
        使用行首匹配的章节标题正则，支持中文和英文格式。
        """
        chapter_pattern = re.compile(
            r'^\s*(?:'
            r'第\s*[零一二三四五六七八九十百千万\d]+\s*[章节部卷]'
            r'|Chapter\s+\d+'
            r'|Part\s+\d+'
            r'|SECTION\s+\d+'
            r')[^\n]*',
            re.IGNORECASE | re.MULTILINE
        )

        matches = list(chapter_pattern.finditer(content))

        if not matches:
            return [{
                'index': 0,
                'title': '全文',
                'start': 0,
                'end': len(content),
                'content': content
            }]

        chapters = []
        for i, match in enumerate(matches):
            title = match.group(0).strip()
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)

            chapters.append({
                'index': i,
                'title': title,
                'start': start,
                'end': end,
                'content': content[start:end]
            })

        return chapters


    def _analyze_paragraphs(self, content, chapters):
        """分析每个段落的人物信息，用于共现计算（带过滤）"""
        paragraphs_info = []

        for chapter in chapters:
            chapter_content = chapter['content']

            paragraphs = chapter_content.split('\n')

            for para_idx, paragraph in enumerate(paragraphs):
                paragraph = paragraph.strip()
                if not paragraph:
                    continue

                chars_in_para = set()
                words = self.cut_text(paragraph)

                for word, flag in words:
                    if flag in ['nr', 'nrf']:
                        if self._is_valid_character_name(word):
                            chars_in_para.add(word)

                if chars_in_para:
                    paragraphs_info.append({
                        'chapter_index': chapter['index'],
                        'paragraph_index': para_idx,
                        'characters': list(chars_in_para),
                        'text': paragraph
                    })

        return paragraphs_info

    def find_character_quotes(self, content, character_name, chapter_idx, paragraphs_info):
        """查找人物在指定章节的相关语句（不限制数量）"""
        quotes = []

        chapter_paragraphs = [
            p for p in paragraphs_info
            if p['chapter_index'] == chapter_idx and character_name in p['characters']
        ]

        for para_info in chapter_paragraphs:
            quotes.append({
                'text': para_info['text'],
                'paragraph_index': para_info['paragraph_index']
            })

        return quotes

