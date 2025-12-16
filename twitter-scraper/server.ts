// 手动定义构建时变量
(global as any).PLATFORM_NODE = true;

import express from 'express';
import cors from 'cors';
import bodyParser from 'body-parser';
import { Scraper } from './src/scraper';
import { HttpsProxyAgent } from 'https-proxy-agent';
import fetch from 'cross-fetch';
import * as dotenv from 'dotenv';
import { Cookie } from 'tough-cookie';

dotenv.config();

const app = express();
const PORT = 3000;

app.use(cors());
app.use(bodyParser.json());

// 代理配置 (如果环境变量 TWITTER_PROXY_URL 存在，则使用)
const PROXY_URL = process.env.TWITTER_PROXY_URL;

app.post('/scrape', async (req, res) => {
    const { username, limit = 20, auth_token, ct0 } = req.body;

    console.log(`[Twitter Scraper] 收到抓取请求: 用户=${username}, 限制=${limit}`);

    if (!username || !auth_token || !ct0) {
        console.error('[Twitter Scraper] 参数缺失');
        return res.status(400).json({ error: 'Missing required fields: username, auth_token, ct0' });
    }

    try {
        // 1. 配置代理 (如果需要)
        let fetchOptions: any = {};
        if (PROXY_URL) {
            console.log(`[Twitter Scraper] 使用代理: ${PROXY_URL}`);
            const agent = new HttpsProxyAgent(PROXY_URL);
            fetchOptions = {
                fetch: (url: string, init: any) => {
                    return fetch(url, {
                        ...init,
                        agent: agent,
                    } as any);
                }
            };
        } else {
            console.log(`[Twitter Scraper] 直连模式 (无代理)`);
        }

        // 2. 初始化 Scraper
        const scraper = new Scraper(fetchOptions);

        // 3. 注入 Cookies
        // 访问私有属性 auth (TypeScript hack)
        const auth = (scraper as any).auth;
        const jar = auth.cookieJar();

        const domain = 'x.com';
        const url = 'https://x.com';

        const authTokenCookie = new Cookie({
            key: 'auth_token',
            value: auth_token,
            domain: domain,
            path: '/',
            secure: true,
            httpOnly: true
        });

        const ct0Cookie = new Cookie({
            key: 'ct0',
            value: ct0,
            domain: domain,
            path: '/',
            secure: true
        });

        jar.setCookieSync(authTokenCookie, url);
        jar.setCookieSync(ct0Cookie, url);

        // 验证 Cookie
        const cookies = await auth.getCookies();
        const hasAuthToken = cookies.some((c: any) => c.key === 'auth_token');
        const hasCt0 = cookies.some((c: any) => c.key === 'ct0');

        if (!hasAuthToken || !hasCt0) {
            console.warn('[Twitter Scraper] 警告: Cookie 注入可能失败');
        }

        // 4. 执行抓取
        console.log(`[Twitter Scraper] 开始抓取 @${username}...`);
        const tweetsGenerator = scraper.getTweets(username, limit);
        const tweets = [];

        for await (const tweet of tweetsGenerator) {
            tweets.push({
                id: tweet.id,
                text: tweet.text,
                timestamp: tweet.timestamp,
                photos: tweet.photos,
                videos: tweet.videos,
                replies: tweet.replies,
                retweets: tweet.retweets,
                likes: tweet.likes,
                views: tweet.views,
                permanentUrl: tweet.permanentUrl,
                isQuoted: tweet.isQuoted,
                isReply: tweet.isReply,
                isRetweet: tweet.isRetweet,
                isPin: tweet.isPin
            });
        }

        console.log(`[Twitter Scraper] 抓取完成，共 ${tweets.length} 条。`);
        return res.json({ success: true, count: tweets.length, tweets: tweets });

    } catch (error: any) {
        console.error('[Twitter Scraper] 抓取失败:', error);
        return res.status(500).json({ error: error.message || 'Internal Server Error' });
    }
});

app.get('/health', (req, res) => {
    res.json({ status: 'ok' });
});

app.listen(PORT, () => {
    console.log(`[Twitter Scraper] 服务运行在端口 ${PORT}`);
    if (PROXY_URL) {
        console.log(`[Twitter Scraper] 代理配置: ${PROXY_URL}`);
    } else {
        console.log(`[Twitter Scraper] 代理配置: 无 (直连)`);
    }
});
