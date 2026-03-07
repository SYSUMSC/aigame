export interface EvaluateExampleCase {
  directoryName: string;
  displayName: string;
  problemScore: number;
  expectsDataset: boolean;
  successLogSnippet: string;
}

export const evaluateExampleCases: EvaluateExampleCase[] = [
  {
    directoryName: 'code_execution_example',
    displayName: '代码执行-线性回归',
    problemScore: 100,
    expectsDataset: true,
    successLogSnippet: '最终得分: max(0, 100 - MSE)',
  },
  {
    directoryName: 'judge_sum',
    displayName: '求和样例',
    problemScore: 1000,
    expectsDataset: false,
    successLogSnippet: '评测完成。共处理',
  },
  {
    directoryName: 'label_compare',
    displayName: '标签比对样例',
    problemScore: 1000,
    expectsDataset: false,
    successLogSnippet: '评测完成。最终得分:',
  },
  {
    directoryName: 'ns_2025_00',
    displayName: '花卉图像分类评测',
    problemScore: 400,
    expectsDataset: false,
    successLogSnippet: '换算得分:',
  },
  {
    directoryName: 'ns_2025_02',
    displayName: '评论违规检测评测',
    problemScore: 400,
    expectsDataset: false,
    successLogSnippet: '总分:',
  },
  {
    directoryName: 'rl_bandit_example',
    displayName: '多臂老虎机样例',
    problemScore: 100,
    expectsDataset: false,
    successLogSnippet: '最终得分 = 100 * 平均奖励率 =',
  },
];

export function getEvaluateExampleCase(directoryName: string): EvaluateExampleCase {
  const exampleCase = evaluateExampleCases.find((entry) => entry.directoryName === directoryName);
  if (!exampleCase) {
    throw new Error(`Unknown evaluate example case: ${directoryName}`);
  }
  return exampleCase;
}
