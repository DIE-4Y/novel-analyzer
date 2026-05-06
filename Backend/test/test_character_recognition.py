# Backend/tests/test_character_recognition.py

import os
import sys
import json


from Backend.utils.novel_processor import NovelProcessor


class CharacterRecognitionTester:
    """人物识别召回率测试器"""

    def __init__(self):
        self.processor = NovelProcessor()

    def calculate_recall(self, predicted_characters, ground_truth_characters):
        """
        计算人物识别召回率

        Args:
            predicted_characters: 系统识别出的人物集合
            ground_truth_characters: 人工标注的真实人物集合

        Returns:
            dict: 包含召回率、精确率等指标的字典
        """
        predicted_set = set(predicted_characters)
        ground_truth_set = set(ground_truth_characters)

        # 正确识别的人物（交集）
        true_positives = predicted_set & ground_truth_set

        # 召回率：系统正确识别的人物数 / 人工标注人物数
        recall = len(true_positives) / len(ground_truth_set) if ground_truth_set else 0

        # 精确率：系统正确识别的人物数 / 系统识别出的总人物数
        precision = len(true_positives) / len(predicted_set) if predicted_set else 0

        # F1 分数
        f1_score = (2 * precision * recall / (precision + recall)
                   if (precision + recall) > 0 else 0)

        # 漏识人物（人工标注了但系统没识别出来）
        missed_characters = ground_truth_set - predicted_set

        # 误识人物（系统识别了但人工没标注）
        false_positives = predicted_set - ground_truth_set

        return {
            'recall': recall,
            'precision': precision,
            'f1_score': f1_score,
            'true_positives': len(true_positives),
            'total_predicted': len(predicted_set),
            'total_ground_truth': len(ground_truth_set),
            'missed_characters': sorted(list(missed_characters)),
            'false_positives': sorted(list(false_positives)),
            'correctly_identified': sorted(list(true_positives))
        }

    def test_single_file(self, filepath, ground_truth_file):
        """
        测试单个文件的人物识别效果

        Args:
            filepath: 小说文件路径
            ground_truth_file: 人工标注文件路径（JSON 格式）

        Returns:
            dict: 测试结果
        """
        print(f"\n{'='*60}")
        print(f"测试文件：{os.path.basename(filepath)}")
        print(f"{'='*60}")

        # 读取人工标注数据
        with open(ground_truth_file, 'r', encoding='utf-8') as f:
            ground_truth_data = json.load(f)

        ground_truth_characters = ground_truth_data.get('characters', [])

        print(f"人工标注人物数：{len(ground_truth_characters)}")
        print(f"人工标注人物：{', '.join(ground_truth_characters[:20])}...")

        # 使用系统识别人物
        print("\n开始识别人物...")
        result = self.processor.process_novel(filepath)
        predicted_characters = list(result['characters'].keys())

        print(f"系统识别人物数：{len(predicted_characters)}")
        print(f"系统识别人物：{', '.join(predicted_characters[:20])}...")

        # 计算召回率
        metrics = self.calculate_recall(predicted_characters, ground_truth_characters)

        # 打印结果
        print(f"\n{'='*60}")
        print("测试结果：")
        print(f"{'='*60}")
        print(f"召回率 (Recall)：{metrics['recall']:.2%}")
        print(f"精确率 (Precision)：{metrics['precision']:.2%}")
        print(f"F1 分数：{metrics['f1_score']:.2%}")
        print(f"\n正确识别：{metrics['true_positives']} 个")
        print(f"系统识别总数：{metrics['total_predicted']} 个")
        print(f"人工标注总数：{metrics['total_ground_truth']} 个")

        if metrics['missed_characters']:
            print(f"\n漏识人物 ({len(metrics['missed_characters'])} 个)：")
            for char in metrics['missed_characters'][:10]:
                print(f"  - {char}")
            if len(metrics['missed_characters']) > 10:
                print(f"  ... 还有 {len(metrics['missed_characters']) - 10} 个")

        if metrics['false_positives']:
            print(f"\n误识人物 ({len(metrics['false_positives'])} 个)：")
            for char in metrics['false_positives'][:10]:
                print(f"  - {char}")
            if len(metrics['false_positives']) > 10:
                print(f"  ... 还有 {len(metrics['false_positives']) - 10} 个")

        return metrics

    def run_batch_tests(self, test_cases):
        """
        批量测试多个文件

        Args:
            test_cases: 测试用例列表，每个元素为 (filepath, ground_truth_file)

        Returns:
            dict: 所有测试的平均指标
        """
        all_metrics = []

        for filepath, ground_truth_file in test_cases:
            try:
                metrics = self.test_single_file(filepath, ground_truth_file)
                all_metrics.append(metrics)
            except Exception as e:
                print(f"\n测试失败：{filepath}")
                print(f"错误信息：{e}")
                import traceback
                traceback.print_exc()

        # 计算平均指标
        if all_metrics:
            avg_recall = sum(m['recall'] for m in all_metrics) / len(all_metrics)
            avg_precision = sum(m['precision'] for m in all_metrics) / len(all_metrics)
            avg_f1 = sum(m['f1_score'] for m in all_metrics) / len(all_metrics)

            print(f"\n{'='*60}")
            print("批量测试总结：")
            print(f"{'='*60}")
            print(f"测试文件数：{len(all_metrics)}")
            print(f"平均召回率：{avg_recall:.2%}")
            print(f"平均精确率：{avg_precision:.2%}")
            print(f"平均 F1 分数：{avg_f1:.2%}")

            return {
                'average_recall': avg_recall,
                'average_precision': avg_precision,
                'average_f1': avg_f1,
                'num_tests': len(all_metrics),
                'individual_results': all_metrics
            }

        return None


def create_sample_ground_truth():
    """
    创建示例人工标注文件的模板
    """
    sample_data = {
        "novel_name": "示例小说",
        "description": "这是人工标注的人物列表",
        "characters": [
            "韩立",
            "南宫婉",
            "厉飞雨",
            "墨大夫",
            "大衍神君"
        ],
        "notes": "请根据实际小说内容填写真实的人物列表"
    }

    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'tests',
        'sample_ground_truth.json'
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)

    print(f"示例人工标注文件已创建：{output_path}")
    print("请根据实际情况修改该文件中的 characters 列表")

    return output_path


if __name__ == '__main__':
    # 创建测试器实例
    tester = CharacterRecognitionTester()

    # 如果需要创建示例标注文件，取消下面的注释
    # create_sample_ground_truth()

    # 单个文件测试示例
    # 你需要准备：
    # 1. 小说文件：Backend/uploads/your_novel.txt
    # 2. 人工标注文件：Backend/tests/ground_truth.json

    novel_file = '../test_data/凡人修仙传(1-100章).txt'

    ground_truth_file = './ground_truth.json'

    # 检查文件是否存在
    if not os.path.exists(novel_file):
        print(f"错误：找不到测试文件 {novel_file}")
        print("请将测试文件放在 Backend/uploads/ 目录下")
        sys.exit(1)

    if not os.path.exists(ground_truth_file):
        print(f"错误：找不到人工标注文件 {ground_truth_file}")
        print("请创建人工标注文件，或使用 create_sample_ground_truth() 生成模板")
        sys.exit(1)

    # 运行测试
    metrics = tester.test_single_file(novel_file, ground_truth_file)

    # 如果需要批量测试，可以这样：
    # test_cases = [
    #     (novel_file_1, ground_truth_file_1),
    #     (novel_file_2, ground_truth_file_2),
    # ]
    # results = tester.run_batch_tests(test_cases)

