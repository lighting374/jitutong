import { expect, test, describe, vi, beforeAll } from 'vitest';
import { mount } from '@vue/test-utils';
import Login from '../src/views/user/Login.vue';
import { setLocale } from '../src/services/locale';

// ----------------------------------------------------
// 关键修复 1：在测试前模拟浏览器环境的语言
// ----------------------------------------------------
beforeAll(() => {
  // 强制设置语言为中文，覆盖 JSDOM 的默认语言
  setLocale('zh');
  // 模拟 navigator.language 为中文 ('zh-CN')，
  // 确保 Login.vue 中的 t() 函数默认返回中文文本
  Object.defineProperty(navigator, 'language', {
    value: 'zh-CN',
    configurable: true,
  });
});

// ----------------------------------------------------
// 关键步骤：模拟所有外部依赖
// ----------------------------------------------------
// 1. 模拟 Vue Router 的 useRouter/push
const mockRouterPush = vi.fn();
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockRouterPush,
  }),
  RouterLink: { template: '<a><slot /></a>' }, // 模拟 RouterLink
}));

// 2. 模拟 API 调用和 Auth 服务
vi.mock('../src/api/user', () => ({
  loginUser: vi.fn(),
}));
vi.mock('../src/services/userAuth', () => ({
  default: { setSession: vi.fn() },
}));
vi.mock('../src/utils/banDetector', () => ({
  startBanDetection: vi.fn(),
}));
// ----------------------------------------------------


describe('Login.vue Component Validation Test', () => {
  
  test('初始渲染时，登录按钮应该显示 "登录"', () => {
    const wrapper = mount(Login);
    // 断言：现在由于我们模拟了中文环境，文本应为中文
    expect(wrapper.find('button[type="submit"]').text()).toContain('登录');
  });

  test('手机号为空时，表单验证应该失败并显示错误信息', async () => {
    const wrapper = mount(Login);
    await wrapper.find('form').trigger('submit.prevent');
    expect(wrapper.vm.phoneError).toBe(wrapper.vm.t('phoneRequired'));
  });

  test('手机号格式不正确时，表单验证应该失败并显示错误信息', async () => {
    const wrapper = mount(Login);
    wrapper.vm.loginForm.phone = '1234567'; 
    await wrapper.find('form').trigger('submit.prevent');
    expect(wrapper.vm.phoneError).toBe(wrapper.vm.t('phoneInvalid'));
  });
  
  test('密码为空时，表单验证应该失败并显示错误信息', async () => {
    const wrapper = mount(Login);
    wrapper.vm.loginForm.phone = '13812345678';
    await wrapper.find('form').trigger('submit.prevent');
    expect(wrapper.vm.passwordError).toBe(wrapper.vm.t('passwordRequired'));
    expect(wrapper.vm.phoneError).toBe(''); 
  });

  test('密码长度小于6位时，表单验证应该失败并显示错误信息', async () => {
    const wrapper = mount(Login);
    wrapper.vm.loginForm.phone = '13812345678';
    wrapper.vm.loginForm.password = '12345'; // 5位密码
    await wrapper.find('form').trigger('submit.prevent');
    expect(wrapper.vm.passwordError).toBe(wrapper.vm.t('passwordTooShort'));
  });

  test('点击 EN 按钮时，应该切换到英文语言', async () => {
    const wrapper = mount(Login);
    // 初始语言为 'zh' 
    expect(wrapper.vm.lang).toBe('zh'); 

    // 找到英文切换按钮并点击
    await wrapper.findAll('button').find(b => b.text() === 'EN')?.trigger('click');
    
    // 修正断言：检查 lang 切换到 'en'
    expect(wrapper.vm.lang).toBe('en');
    // 断言：欢迎标题变为英文
    expect(wrapper.find('h1').text()).toContain('Welcome back');
  });
});