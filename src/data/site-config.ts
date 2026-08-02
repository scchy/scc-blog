import avatar from '../assets/images/avatar.jpg';
import hero from '../assets/images/hero.jpg';
import type { SiteConfig } from '../types';

const siteConfig: SiteConfig = {
    website: 'https://scchy.github.io',
    avatar: {
        src: avatar,
        alt: 'SCC 的头像'
    },
    title: 'SCC 的博客',
    subtitle: '记录技术、思考与成长的开发者博客',
    description: 'SCC 的个人开发者博客，记录技术、产品与个人成长。',
    image: {
        src: '/dante-preview.jpg',
        alt: 'SCC 的博客'
    },
    headerNavLinks: [
        {
            text: '首页',
            href: '/scc-blog/'
        },
        {
            text: '作品集',
            href: '/scc-blog/projects'
        },
        {
            text: '博客',
            href: '/scc-blog/blog'
        },
        {
            text: '主题',
            href: '/scc-blog/topics'
        },
        {
            text: '标签',
            href: '/scc-blog/tags'
        }
    ],
    footerNavLinks: [
        {
            text: '关于',
            href: '/scc-blog/about'
        },
        {
            text: '联系',
            href: '/scc-blog/contact'
        },
        {
            text: '条款',
            href: '/scc-blog/terms'
        },
        {
            text: 'GitHub',
            href: 'https://github.com/scchy/scc-blog'
        }
    ],
    socialLinks: [
        {
            text: 'GitHub',
            href: 'https://github.com/scchy'
        },
        {
            text: 'X/Twitter',
            href: 'https://twitter.com/'
        }
    ],
    hero: {
        title: '你好，欢迎来到我的博客！',
        text: "我是 **SCC**，一名开发者。\n这个博客记录我在技术、产品和个人成长方面的思考。\n\n内容首发于此，同步分发到 Dev.to 与掘金，欢迎常来看看。",
        image: {
            src: hero,
            alt: 'SCC 的羊毛毡头像'
        },
        actions: [
            {
                text: '联系我',
                href: '/scc-blog/contact'
            }
        ]
    },
    subscribe: {
        enabled: false,
        title: '订阅更新',
        text: '每周一篇，最新文章直达邮箱。',
        form: {
            action: '#'
        }
    },
    postsPerPage: 8,
    projectsPerPage: 8
};

export default siteConfig;
