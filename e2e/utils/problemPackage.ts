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

export interface BuiltPackagedExampleArchive extends BuiltProblemArchive {
  stagedProblemDir: string;
  submissionZipPath: string;
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

async function zipDirectoryContents(sourceDir: string, outZipPath: string): Promise<void> {
  await fs.rm(outZipPath, { force: true });
  await execFileAsync('zip', ['-qr', outZipPath, '.', '-x', '*.zip'], { cwd: sourceDir });
}

async function hasFiles(directoryPath: string): Promise<boolean> {
  try {
    const entries = await fs.readdir(directoryPath);
    return entries.length > 0;
  } catch {
    return false;
  }
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

// 按 evaluate_example 的目录规范重新生成 judge.zip / test_submit.zip，再打出最终题目包。
export async function buildPackagedProblemFromExample(
  exampleDir: string,
  options: ProblemArchiveOptions & { taskDirName?: string },
): Promise<BuiltPackagedExampleArchive> {
  const tempRoot = await fs.mkdtemp(path.join(os.tmpdir(), 'aigame-e2e-packaged-problem-'));
  const stagingRoot = path.join(tempRoot, 'staging');
  const taskDirName = options.taskDirName ?? path.basename(exampleDir);
  const stagedProblemDir = path.join(stagingRoot, taskDirName);
  const archivePath = path.join(tempRoot, `${options.archiveName}.zip`);
  const judgeZipPath = path.join(stagedProblemDir, 'judge.zip');
  const submissionZipPath = path.join(stagedProblemDir, 'test_submit.zip');
  const dataZipPath = path.join(stagedProblemDir, 'data.zip');

  await fs.mkdir(stagingRoot, { recursive: true });
  await fs.cp(exampleDir, stagedProblemDir, { recursive: true });

  await Promise.all([
    fs.writeFile(path.join(stagedProblemDir, 'problem.yml'), renderProblemYaml(options), 'utf8'),
    fs.writeFile(path.join(stagedProblemDir, 'desc.md'), options.detailedDescription, 'utf8'),
    fs.rm(judgeZipPath, { force: true }),
    fs.rm(submissionZipPath, { force: true }),
    fs.rm(dataZipPath, { force: true }),
    fs.rm(path.join(stagedProblemDir, `${taskDirName}.zip`), { force: true }),
  ]);

  await zipDirectoryContents(path.join(stagedProblemDir, 'judge'), judgeZipPath);
  await zipDirectoryContents(path.join(stagedProblemDir, 'test_submit'), submissionZipPath);

  const packageEntries = ['problem.yml', 'desc.md', 'judge.zip', 'test_submit.zip'];
  if (await hasFiles(path.join(stagedProblemDir, 'data'))) {
    await zipDirectoryContents(path.join(stagedProblemDir, 'data'), dataZipPath);
    packageEntries.push('data.zip');
  }

  await execFileAsync('zip', ['-qj', archivePath, ...packageEntries], { cwd: stagedProblemDir });

  return {
    archivePath,
    stagedProblemDir,
    submissionZipPath,
    cleanup: async () => {
      await fs.rm(tempRoot, { recursive: true, force: true });
    },
  };
}
