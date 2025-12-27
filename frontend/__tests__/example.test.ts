// __tests__/example.test.ts

import { expect, test } from 'vitest';

// 这是一个简单的通过测试，用于验证 CI 环境配置是否成功
test('Vitest environment is running correctly', () => {
  // 确保测试总是通过
  expect(1 + 1).toBe(2);
});