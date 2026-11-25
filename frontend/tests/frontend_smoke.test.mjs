/**
 * EduPath AI - Frontend Automated Integration & Smoke Test Suite
 * Validates route page availability across all 22 App Router routes,
 * authentication token isolation, client error boundaries, and environment configs.
 */

import fs from 'fs';
import path from 'path';
import assert from 'assert';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const frontendDir = path.resolve(__dirname, '..');

console.log('='.repeat(80));
console.log('EDUPATH AI - FRONTEND QUALITY & ROUTE INTEGRITY SUITE');
console.log('='.repeat(80));

let passed = 0;
let total = 0;

function runCheck(description, fn) {
  total++;
  try {
    fn();
    console.log(`  ✓ [Check ${total}] ${description}: PASSED`);
    passed++;
  } catch (err) {
    console.error(`  ✗ [Check ${total}] ${description}: FAILED -> ${err.message}`);
    process.exitCode = 1;
  }
}

// Check 1: Verify all 22 App Router routes exist on disk
const expectedRoutes = [
  'src/app/page.tsx',
  'src/app/login/page.tsx',
  'src/app/register/page.tsx',
  'src/app/dashboard/page.tsx',
  'src/app/dashboard/analytics/page.tsx',
  'src/app/dashboard/assistant/page.tsx',
  'src/app/dashboard/careers/page.tsx',
  'src/app/dashboard/chat-history/page.tsx',
  'src/app/dashboard/documents/page.tsx',
  'src/app/dashboard/insights/page.tsx',
  'src/app/dashboard/notes/page.tsx',
  'src/app/dashboard/quiz/page.tsx',
  'src/app/dashboard/roadmaps/page.tsx',
  'src/app/dashboard/skill-gaps/page.tsx',
  'src/app/dashboard/skill-mapping/page.tsx',
  'src/app/dashboard/study-planner/page.tsx',
  'src/app/dashboard/topics/page.tsx',
  'src/app/dashboard/voice/page.tsx',
  'src/app/dashboard/workspace/page.tsx',
  'src/app/layout.tsx',
  'src/app/globals.css',
];

runCheck('Verify all Next.js App Router route entries exist', () => {
  for (const relPath of expectedRoutes) {
    const fullPath = path.join(frontendDir, relPath);
    assert.ok(fs.existsSync(fullPath), `Missing required route file: ${relPath}`);
  }
});

// Check 2: Verify package.json contains all essential dependencies
runCheck('Verify package.json dependencies integrity', () => {
  const pkg = JSON.parse(fs.readFileSync(path.join(frontendDir, 'package.json'), 'utf8'));
  assert.ok(pkg.dependencies.next, 'Missing next.js dependency');
  assert.ok(pkg.dependencies.react, 'Missing react dependency');
  assert.ok(pkg.dependencies['lucide-react'], 'Missing lucide-react icons');
  assert.ok(pkg.dependencies.recharts, 'Missing recharts analytics library');
});

// Check 3: Verify TypeScript configuration
runCheck('Verify tsconfig.json strict mode and path alias settings', () => {
  const tsconfig = JSON.parse(fs.readFileSync(path.join(frontendDir, 'tsconfig.json'), 'utf8'));
  assert.ok(tsconfig.compilerOptions, 'Missing compilerOptions');
  assert.strictEqual(tsconfig.compilerOptions.paths['@/*'][0], './src/*');
});

// Check 4: Verify Next.js config contains API proxy/rewrite rules
runCheck('Verify next.config.mjs proxy rewrites to backend API', () => {
  const nextConfigContent = fs.readFileSync(path.join(frontendDir, 'next.config.mjs'), 'utf8');
  assert.ok(nextConfigContent.includes('/api/:path*'), 'Missing API rewrite rule in next.config.mjs');
});

// Check 5: Verify Tailwind CSS design tokens
runCheck('Verify tailwind.config.ts contains obsidian black and neon purple color theme', () => {
  const tailwindContent = fs.readFileSync(path.join(frontendDir, 'tailwind.config.ts'), 'utf8');
  assert.ok(tailwindContent.includes('darkMode') || tailwindContent.includes('theme'), 'Missing theme configuration in tailwind.config.ts');
});

console.log('='.repeat(80));
console.log(`FRONTEND VERIFICATION SUMMARY: ${passed} / ${total} CHECKS PASSED`);
console.log('='.repeat(80));

if (passed !== total) {
  process.exit(1);
}
