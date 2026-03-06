import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const execFileAsync = promisify(execFile);

export interface ProblemArchiveOptions {
  archiveName: string;
  title: string;
  shortDescription: string;
  startTime: string;
  endTime: string;
  score: number;
  detailedDescription: string;
}

export interface BuiltProblemArchive {
  archivePath: string;
  cleanup: () => Promise<void>;
}

function renderProblemYaml(options: ProblemArchiveOptions): string {
  return [
    `title: \"${options.title}\"`,
    `shortDescription: \"${options.shortDescription}\"`,
    `startTime: \"${options.startTime}\"`,
    `endTime: \"${options.endTime}\"`,
    `score: ${options.score}`,
    '',
  ].join('\n');
}

// 基于现有样例目录生成一个可上传的题目压缩包，便于覆盖新增与覆盖更新分支。
export async function buildProblemArchiveFromExample(
  exampleDir: string,
  options: ProblemArchiveOptions,
): Promise<BuiltProblemArchive> {
  const tempRoot = await fs.mkdtemp(path.join(os.tmpdir(), 'aigame-e2e-problem-'));
  const workDir = path.join(tempRoot, 'content');
  const archivePath = path.join(tempRoot, `${options.archiveName}.zip`);

  await fs.cp(exampleDir, workDir, { recursive: true });
  await fs.writeFile(path.join(workDir, 'problem.yml'), renderProblemYaml(options), 'utf8');
  await fs.writeFile(path.join(workDir, 'desc.md'), options.detailedDescription, 'utf8');
  await execFileAsync('zip', ['-qr', archivePath, '.'], { cwd: workDir });

  return {
    archivePath,
    cleanup: async () => {
      await fs.rm(tempRoot, { recursive: true, force: true });
    },
  };
}
