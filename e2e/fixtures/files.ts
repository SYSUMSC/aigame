import path from 'node:path';
import { getRepoRoot } from '../utils/runtime';

const repoRoot = getRepoRoot();
const evaluateExampleRoot = path.join(repoRoot, 'evaluate_example');

// 评测链路与批量题目上传会复用这些样例文件。
export const sampleFiles = {
  judgeZip: path.join(repoRoot, 'evaluate_example/judge_sum/judge.zip'),
  submissionZip: path.join(repoRoot, 'evaluate_example/judge_sum/test_submit.zip'),
  judgeSumDir: path.join(evaluateExampleRoot, 'judge_sum'),
};
