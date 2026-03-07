import { test } from '@playwright/test';
import { getEvaluateExampleCase } from './cases';
import { runEvaluateExampleCase } from './shared';

test('ns_2025_00 可以完成上传与示例提交', async ({}, testInfo) => {
  test.setTimeout(240_000);
  await runEvaluateExampleCase(getEvaluateExampleCase('ns_2025_00'), testInfo);
});
