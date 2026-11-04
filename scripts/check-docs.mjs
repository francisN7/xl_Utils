#!/usr/bin/env node
/**
 * Confere a saúde da documentação sem dependências:
 *
 * 1. links relativos entre arquivos `.md` (ignora http(s), mailto e #âncora);
 * 2. orçamento de linhas de AGENTS, CURRENT e specs de sessão;
 * 3. histórico disfarçado de referência ("## Cobertura da SXX").
 *
 * Histórico: CHANGELOG, `docs/releases/` e ADRs não entram na checagem de link.
 * Specs de fases fechadas saem do working tree; o orçamento vale para as que
 * ficam (a próxima e as em andamento).
 *
 * Uso: node scripts/check-docs.mjs
 */

import { existsSync, readdirSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

const SKIP_DIRS = new Set([
  '.git',
  '.expo',
  'backups',
  'dist',
  'dist-web',
  'node_modules',
  'tmp',
  '.temp',
  '.venv',
]);

/** Documentos históricos: não são reescritos nem têm links cobrados. */
const SKIP_LINKS = ['CHANGELOG.md', 'docs/sessions/', 'docs/adr/'];

const BUDGETS = [
  { file: 'AGENTS.md', max: 100 },
  { file: 'docs/state/CURRENT.md', max: 60 },
];

const errors = [];
let checkedFiles = 0;
let checkedLinks = 0;

function walk(dir) {
  const entries = readdirSync(dir, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    if (entry.isDirectory()) {
      if (SKIP_DIRS.has(entry.name)) continue;
      files.push(...walk(path.join(dir, entry.name)));
    } else if (entry.name.endsWith('.md')) {
      files.push(path.join(dir, entry.name));
    }
  }
  return files;
}

function relative(file) {
  return path.relative(root, file).replaceAll('\\', '/');
}

function lineCount(file) {
  const text = readFileSync(file, 'utf8').replace(/\r?\n$/, '');
  return text.split(/\r?\n/).length;
}

function checkLinks(file) {
  const rel = relative(file);
  if (SKIP_LINKS.some((skip) => rel === skip || rel.startsWith(skip))) return;

  const text = readFileSync(file, 'utf8');
  const lines = text.split(/\r?\n/);
  const linkPattern = /\]\(([^)\s]+)\)/g;
  const imagePattern = /<img[^>]+src="([^"]+)"/gi;

  const checkTarget = (target, lineNumber) => {
    if (/^(https?:|mailto:|#|<)/.test(target)) return;
    checkedLinks += 1;
    const clean = decodeURI(target.split('#')[0].split('?')[0]);
    if (!clean) return;
    const resolved = path.resolve(path.dirname(file), clean);
    if (!existsSync(resolved)) {
      errors.push(`${rel}:${lineNumber} link quebrado -> ${target}`);
    }
  };

  lines.forEach((line, index) => {
    for (const match of line.matchAll(linkPattern)) {
      checkTarget(match[1], index + 1);
    }
    for (const match of line.matchAll(imagePattern)) {
      checkTarget(match[1], index + 1);
    }
  });
}

function checkBudget(file) {
  const rel = relative(file);
  const budget = BUDGETS.find((item) => item.file === rel);
  if (budget) {
    const lines = lineCount(file);
    if (lines > budget.max) {
      errors.push(`${rel}: ${lines} linhas (máx. ${budget.max})`);
    }
  }
}

function checkSessionBudget(file) {
  const rel = relative(file);
  if (!rel.startsWith('docs/sessions/') || rel.endsWith('_TEMPLATE.md')) return;
  const lines = lineCount(file);
  if (lines > 90) {
    errors.push(`${rel}: ${lines} linhas (spec máx. 90)`);
  }
}

function checkReferenceHistory(file) {
  const rel = relative(file);
  if (!rel.startsWith('docs/reference/')) return;
  const text = readFileSync(file, 'utf8');
  for (const match of text.matchAll(
    /^##+\s+(Cobertura da S.+|S\d+[a-z]?\b.*)$/gim,
  )) {
    errors.push(`${rel}: heading de histórico -> "${match[0].trim()}"`);
  }
}

const files = walk(root);

for (const file of files) {
  checkedFiles += 1;
  checkLinks(file);
  checkBudget(file);
  checkSessionBudget(file);
  checkReferenceHistory(file);
}

if (errors.length > 0) {
  console.error(
    `docs: ${errors.length} problema(s) em ${checkedFiles} arquivos`,
  );
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log(
  `docs ok: ${checkedFiles} arquivos, ${checkedLinks} links, orçamentos e referência limpos`,
);
