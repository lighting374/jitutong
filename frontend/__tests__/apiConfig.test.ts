import { expect, test, describe, beforeEach } from 'vitest';
// 导入要测试的函数和常量。注意导入路径需要是相对路径。
import { API_CONFIG, getBackendUrl, fixAvatarUrl } from '../src/config/apiConfig'; 

// 假设 BACKEND_URL 的值为 'http://192.168.3.197:5000'

describe('API Configuration Utilities Test', () => {
  // 在每个测试开始前，我们可以固定一下 BACKEND_URL 的值，确保测试环境一致
  const MOCK_BACKEND_URL = 'http://test-server:5000';
  
  beforeEach(() => {
    // 临时修改 API_CONFIG 以进行稳定测试
    API_CONFIG.BACKEND_URL = MOCK_BACKEND_URL;
  });

  // --- getBackendUrl 函数测试 ---
  describe('getBackendUrl', () => {
    test('应该返回不带路径的完整后端 URL', () => {
      // getBackendUrl()
      expect(getBackendUrl()).toBe(MOCK_BACKEND_URL);
    });

    test('应该将相对路径正确拼接为完整 URL（不带开头的 /）', () => {
      // getBackendUrl('api/users')
      expect(getBackendUrl('api/users')).toBe(`${MOCK_BACKEND_URL}/api/users`);
    });

    test('应该将相对路径正确拼接为完整 URL（带开头的 /）', () => {
      // getBackendUrl('/api/posts')
      expect(getBackendUrl('/api/posts')).toBe(`${MOCK_BACKEND_URL}/api/posts`);
    });

    test('如果输入已经是完整 URL，则应直接返回', () => {
      const fullUrl = 'https://external.cdn.com/data.json';
      expect(getBackendUrl(fullUrl)).toBe(fullUrl);
      
      const fullUrlHttp = 'http://external.cdn.com/data.json';
      expect(getBackendUrl(fullUrlHttp)).toBe(fullUrlHttp);
    });
  });

  // --- fixAvatarUrl 函数测试 ---
  describe('fixAvatarUrl', () => {
    test('如果头像路径是 undefined 或 null，应返回默认路径', () => {
      // fixAvatarUrl(undefined)
      expect(fixAvatarUrl(undefined)).toBe('/avatar.jpg');
      // fixAvatarUrl(null)
      expect(fixAvatarUrl(null as any)).toBe('/avatar.jpg'); // TypeScript 类型处理
    });

    test('如果头像路径是完整 URL，则应直接返回', () => {
      const externalUrl = 'https://qq.com/user/avatar.png';
      expect(fixAvatarUrl(externalUrl)).toBe(externalUrl);
    });

    test('应该将相对路径正确拼接为完整的头像 URL', () => {
      // 假设传入的是后端存储的相对路径，例如 'uploads/user/1.jpg'
      const relativePath = 'uploads/user/1.jpg';
      expect(fixAvatarUrl(relativePath)).toBe(`${MOCK_BACKEND_URL}/${relativePath}`);
    });
    
    test('应该处理以 / 开头的相对路径', () => {
      // 假设传入的是后端存储的相对路径，例如 '/uploads/user/1.jpg'
      const relativePath = '/uploads/user/1.jpg';
      expect(fixAvatarUrl(relativePath)).toBe(`${MOCK_BACKEND_URL}${relativePath}`);
    });
  });
});