import path from 'node:path';
import { getRepoRoot } from '../utils/runtime';

const repoRoot = getRepoRoot();

// 评测链路使用的样例文件。
export const sampleFiles = {
  judgeZip: path.join(repoRoot, 'evaluate_example/judge_sum/judge_sum.zip'),
  submissionZip: path.join(repoRoot, 'evaluate_example/judge_sum/test_submit.zip'),
};
