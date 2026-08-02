export interface Topic {
    slug: string;
    title: string;
    subtitle: string;
    description: string;
    tags: string[];
}

export const topics: Topic[] = [
    {
        slug: 'rl',
        title: '强化学习',
        subtitle: 'Reinforcement Learning',
        description: '马尔可夫决策过程、策略梯度、Q-Learning、深度强化学习（DQN/PPO/SAC）等算法与工程实践。',
        tags: ['RL', '强化学习', 'MDP', 'PPO', 'DQN']
    },
    {
        slug: 'llm-agent',
        title: 'LLM + Agent',
        subtitle: 'Large Language Model & Agent',
        description: '大语言模型应用、Prompt Engineering、Agent 架构、工具调用、RAG、多智能体协作与工程落地。',
        tags: ['LLM', 'Agent', '大模型', 'RAG', 'Prompt']
    },
    {
        slug: 'ml-dl',
        title: '机器学习与深度学习',
        subtitle: 'Machine Learning & Deep Learning',
        description: '传统机器学习、神经网络、模型训练与调优、特征工程、分布式训练与推理优化。',
        tags: ['ML', '深度学习', '机器学习', '神经网络', 'Transformer']
    },
    {
        slug: 'parenting',
        title: '亲子成长',
        subtitle: 'Parenting & Family',
        description: '亲子英语学习、儿童教育游戏、家庭教育方法、高质量陪伴与成长记录。',
        tags: ['亲子', '英语学习', '教育', '游戏', '家庭']
    },
    {
        slug: 'experience',
        title: '经验分享',
        subtitle: 'Experience & Insights',
        description: '个人成长、学习工作方法、工具使用与项目实战的经验总结与复盘。',
        tags: ['经验分享', '博客', 'Astro', 'GitHub Pages', 'SEO', '工作流', '复盘', '工具']
    }
];
