let userPhone = []
if (process?.env?.dx) {
    process?.env?.dx.split('\n').map(item => {
        if (item) {
            let phone = item.split('#')[0]
            let password = item.split('#')[1]
            userPhone.push({ phone, password })
        }
    })
} else {
    console.log('未找到环境变量，请设置环境变量dx')
    process.exit()
    return
} 
let userName = ''
if (process?.env?.dxUserName) {
    userName=process?.env?.dxUserName
} else {
    console.log('未找到环境变量，请设置环境变量dxUserName')
    process.exit()
    return
}
const axios = require('axios')
const tool = require('./tools/tool.js')
const { v4 } = require('uuid');
const fs = require('fs')
const JSEncrypt = require('node-jsencrypt');
const nodeRsa = require('node-rsa');
let pubKey = `MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB`
const decrypt = new JSEncrypt(); // 创建加密对象实例
decrypt.setPrivateKey(pubKey)
// let pubKey2 = `MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIPOHtjs6p4sTlpFvrx+ESsYkEvyT4JB/dcEbU6C8+yclpcmWEvwZFymqlKQq89laSH4IxUsPJHKIOiYAMzNibhED1swzecH5XLKEAJclopJqoO95o8W63Euq6K+AKMzyZt1SEqtZ0mXsN8UPnuN/5aoB3kbPLYpfEwBbhto6yrwIDAQAB`
// const decrypt2 = new JSEncrypt(); // 创建加密对象实例
// decrypt2.setPrivateKey(pubKey2)
let keyContent = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIPOHtjs6p4sTlpFvrx+ESsYkEvyT4JB/dcEbU6C8+yclpcmWEvwZFymqlKQq89laSH4IxUsPJHKIOiYAMzNibhED1swzecH5XLKEAJclopJqoO95o8W63Euq6K+AKMzyZt1SEqtZ0mXsN8UPnuN/5aoB3kbPLYpfEwBbhto6yrwIDAQAB"
let resKey = "-----BEGIN PUBLIC KEY-----\n" + keyContent + "\n-----END PUBLIC KEY-----"
let rsaJiami = new nodeRsa(resKey);
const encryptionScheme = {
    encryptionScheme: "pkcs1"
};
rsaJiami.setOptions(encryptionScheme);
let pushAppToken = 'AT_P1ULOqqGLgyD1CVKfjYJqhWWtTUwHKQk' //推送apptoken WXpush申请

// 直播列表
let liveListAll=[]
// 可抽奖列表
let goodList = []
let isGetLive = false
let pushArr={}
let sendTxt={}
let runGameId=[]
async function sendMsg(content, uuid) {
    const options = {
        url: 'https://wxpusher.zjiecode.com/api/send/message',
        method: 'post',
        headers: {
            'Content-Type': 'application/json',
        },
        data: {
            "appToken": pushAppToken,
            "content": content,
            "summary": `星播客中奖`,
            "contentType": 2,
            "topicIds": [],
            "uids": [
                uuid
            ],
            "verifyPayType": '2'
        }
    }
    const response = await axios(options)
    console.log(response.data);
    return response.data
}
async function getUsercode(ticket) {
    try {
        const options = {
            method: "get",
            url: "https://xbk.189.cn/xbkapi/api/auth/jump",
            params: {
                userID: ticket,
                version: '9.3.3',
                type: 'room',
                l: 'renwu',
            },
            headers: {
                'User-Agent': 'Mozilla/5.0 (Linux; U; Android 12; zh-cn; ONEPLUS A9000 Build/QKQ1.190716.003) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1'
            }
        };
        let res = await axios(options)
        let url = res.request.path
        let params = url.split('?')[1].split('&')
        let usercode = ''
        params.map(item => {
            if (item.split('=')[0] == 'usercode') {
                usercode = item.split('=')[1]
            }
        })
        // console.log(usercode);
        return usercode
    } catch (e) {
        return await getUsercode(ticket)
    }
}
async function getToken(usercode) {
    try {
        const options = {
            method: "post",
            url: "https://xbk.189.cn/xbkapi/api/auth/userinfo/codeToken",
            data: {
                usercode: usercode
            },
            headers: {
                'User-Agent': 'Mozilla/5.0 (Linux; U; Android 12; zh-cn; ONEPLUS A9000 Build/QKQ1.190716.003) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1'
            }
        };
        let res = await axios(options)
        // console.log(res.data);
        return res.data.data.token
    } catch (e) {
        return await getToken(usercode)
    }
}
let cacheLive=[]
// 初始化直播间数据
async function initFloor(provinceCode, page, khd, token) {
    if(provinceCode==1&&page==1&&khd==1){
        cacheLive=[]
    }
    return new Promise(async (resolve, reject) => {
        // getLive = true
        try {
            const options = {
                method: "get",
                url: `https://xbk.189.cn/xbkapi/api/room/index/floor?provinceCode=${provinceCode < 10 ? '0' + provinceCode : provinceCode + ''}&pageType=1&page=${page}&khd=${khd}`,
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Linux; U; Android 12; zh-cn; ONEPLUS A9000 Build/QKQ1.190716.003) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1',
                    'Authorization': 'Bearer ' + rsaJiami.encrypt(token, 'base64')
                }
            };
            let res = await axios(options)
            let time = new Date().valueOf()
            // console.log(res.data);
            res?.data?.data?.map(item => {
                if (item.liveType == 2 || item.liveType == 1) {
                   let newtime = new Date(item.liveStartTime.replace(/-/g, "/")).valueOf()
                    if ((time - 1000 * 60 * 60 * 24*7) < newtime) {
                        cacheLive.push(item)
                    }
                }
            })
            // 加载下一页直播间数据
            async function nextList(provinceCode, page, khd, token) {
                try {
                    page++
                    const options = {
                        method: "get",
                        url: `https://xbk.189.cn/xbkapi/api/room/index/floor?provinceCode=${provinceCode < 10 ? '0' + provinceCode : provinceCode + ''}&pageType=1&page=${page}&khd=${khd}`,
                        headers: {
                            'User-Agent': 'Mozilla/5.0 (Linux; U; Android 12; zh-cn; ONEPLUS A9000 Build/QKQ1.190716.003) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1',
                            'Authorization': 'Bearer ' + rsaJiami.encrypt(token, 'base64')
                        }
                    };
                    let res = await axios(options)
                    let time = new Date().valueOf()
                    let liveStart = 0
                    res?.data?.data?.map(item => {
                        if (item.liveType == 2 || item.liveType == 1) {
                            let newtime = new Date(item.liveStartTime.replace(/-/g, "/")).valueOf()
                            if ((time - 1000 * 60 * 60 * 24 * 7) < newtime) {
                                cacheLive.push(item)
                            }
                            liveStart++
                        }
                    })
                    if (liveStart > 0) {
                        nextList(provinceCode, page, khd, token)
                    } else if (Number(provinceCode) == 36) {
                        cacheLive = fn2(cacheLive)
                        cacheLive.sort((a, b) => {
                            let at = new Date(a.liveStartTime.replace(/-/g, "/")).valueOf()
                            let bt = new Date(b.liveStartTime.replace(/-/g, "/")).valueOf()
                            return at - bt
                        })
                        cacheLive.sort((a, b) => {
                            return b.liveType - a.liveType
                        })
                        // getLive = false
                        // console.log(liveList);

                        console.log('直播间获取完成', cacheLive.length, '个');
                        fs.writeFileSync('./liveList.json', JSON.stringify(cacheLive), 'utf8')
                        liveListAll = JSON.parse(fs.readFileSync('./liveList.json', 'utf8'));
                        console.log('直播间写入本地完成', liveListAll.length, '个');
                        resolve(cacheLive)
                    } else if (provinceCode < 36) {
                        if (khd == 1) {
                            khd = 2
                            resolve(await initFloor(provinceCode, 1, khd, token))
                        } else if (khd == 2) {
                            console.log('获取所有直播间进度', Math.floor((provinceCode / 36) * 100) + '%')
                            khd = 1
                            provinceCode += 1
                            resolve(await initFloor(provinceCode, 1, khd, token))
                        }
                    }
                } catch (e) {
                    // console.log(e);
                    await nextList(provinceCode, page, khd, token)
                }
            }
            await nextList(provinceCode, page, khd, token)
        } catch (e) {
            // console.log(e);
            resolve(await initFloor(provinceCode, page, khd, token))
        }
    })
}

// 获取直播间商品
async function getGoodList(liveId, page, token) {
    try {
        const options = {
            method: "get",
            url: `https://xbk.189.cn/xbkapi/lteration/room/getLiveGoodsList?liveId=${liveId}&list_type=ordinary&page=${page}`,
            headers: {
                'User-Agent': 'Mozilla/5.0 (Linux; U; Android 12; zh-cn; ONEPLUS A9000 Build/QKQ1.190716.003) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1',
                'Authorization': 'Bearer ' + rsaJiami.encrypt(token, 'base64')
            }
        };
        let res = await axios(options)
        return res.data
    } catch (e) {
        // console.log();
    }
}
async function getFile() {
    try {
        const uuidV4 = v4();
        let options = {
            url: `https://xbk.189.cn/xbkapi/api/auth/captcha?guid=${uuidV4}`,
            method: 'GET',
            responseType: 'arraybuffer'  // 设置响应类型为arraybuffer
        }
        let res = await axios(options)
        // console.log(res.data);
        // 将二进制数据转换为Base64字符串
        const base64Data = Buffer.from(res.data, 'binary').toString('base64');
        // console.log(base64Data);
        return {
            file: res.data,
            base64: 'data:image/png;base64,' + base64Data,
            uuid: uuidV4
        }
    } catch (e) {
        return await getFile()
    }
}
async function getOcr() {
    try {
        let getFiles = await getFile()
        let options = {
            url: `http://8.137.117.207:8677/ocr`,
            method: 'post',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data: {
                // file:(await getFile()).file,
                image: getFiles.base64,
                userName:userName
            }
        }
        // image:'data:image/png;base64,'+(await getFile()).base64,
        // console.log(options);
        let res = await axios(options)
        if (res.data.code == 200) {
            let data = res.data.data
            let splitData=data.split('=')
            let numberStr=''
            if(splitData.length>1){
                numberStr=splitData[0]
            }else{
                numberStr=data.split('x')[0]+'+'+data.split('x')[1]
            }
            let number = eval(`${numberStr}`)
            // console.log(number);
            // console.log(getFiles.base64);
            return {
                data:number,
                uuid: getFiles.uuid,
            }
        }
    } catch (e) {
        return await getOcr()
    }
}
// 直播间抽奖
async function lotteryDo(liveId, active_code, token, phone,uid) {
    try {
        let captchaData = await getOcr()
        // console.log(captchaData);
        // return
        let options = {
            method: "post",
            url: `https://xbk.189.cn/xbkapi/active/v2/lottery/do`,
            headers: {
                'User-Agent': 'Mozilla/5.0 (Linux; U; Android 12; zh-cn; ONEPLUS A9000 Build/QKQ1.190716.003) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1',
                'Authorization': 'Bearer ' + rsaJiami.encrypt(token, 'base64')
            },
            data: {
                "active_code": active_code,
                "captcha": captchaData.data,
                "guid": captchaData.uuid,
                "liveId": liveId,
                "period": "1"
            }
        };
        // console.log(options);
        let res = await axios(options)
        // if (res?.data?.msg?.includes('图形验证码校验未通过')) {
        //     return await lotteryDo(liveId, active_code, token, phone)
        // } else {
        //     console.log(res?.data?.data?.title||res?.data?.msg, tool.maskPhone(phone));
        // }
        if (res?.data?.msg === 'success') {
            const title = res?.data?.data?.title;
            console.log(`抽奖成功, 获得: ${title}, 手机号: ${tool.maskPhone(phone)}`);
            pushArr[uid][phone]=`<div>手机号: ${tool.maskPhone(phone)},抽奖成功, 获得:<span style="color: red;">${title}</span></div>`
        } else if (res?.data?.msg === '抽奖机会不足') {
            // console.log(`抽奖机会不足，停止当前账号操作: ${tool.maskPhone(phone)}`);
        } else if (res?.data?.msg === '图形验证码校验未通过') {
            // console.log(`图形验证码校验未通过，正在重试...: ${tool.maskPhone(phone)}`);
            await tool.wait(6000)
            lotteryDo(liveId, active_code, token, phone); // 递归调用尝试再次执行
        } else if (res?.data?.msg?.includes('操作过于频繁')) {
            // console.log(`操作过于频繁，正在重试...: ${tool.maskPhone(phone)}`);
            await tool.wait(6000)
            lotteryDo(liveId, active_code, token, phone); // 递归调用尝试再次执行
        }else{
            // console.log(res?.data?.data?.title||res?.data?.msg, tool.maskPhone(phone))
        }
        // return res.data
    } catch (e) {
        // console.log(e);
        lotteryDo(liveId, active_code, token, phone)
    }
}
function extractNumbersWithDecimalsAndNegatives(text) {
    // 定义正则表达式，用于匹配带小数点和负号的数字
    const regex = /-?\d+(\.\d+)?/g;
    
    // 使用正则表达式进行匹配，并将结果转换为数组
    const matches = text.match(regex);
    
    // 如果有匹配项，返回匹配到的数字数组，并转换为浮点数；否则返回空数组
    return matches ? matches.map(Number) : [];
}

async function getStart(token) {
    let goodlist = []
    const currentDate = new Date();
    const dayOfMonth = currentDate.getDate();
    let listLives=JSON.parse(JSON.stringify(liveListAll))
    // for (let i = 0; i < listLives.length; i++) {
    //     let data = await getGoodList(listLives[i].liveId, 1, token)

    //     if (data?.data?.list?.length == data?.data?.count) {
    //         // console.log('直播间商品列表返回和实际数量一样');
    //         data?.data?.list?.map(async item => {
    //             if (item.activeCode) {
    //                 item.liveId = listLives[i]?.liveId
    //                 goodlist.push(item)
    //                 console.log('有抽奖',item.liveId,item.title,item.activeCode);
    //                 goAllLottery([item])
    //                 // let maxNumber = await prizeList(token, item.activeCode, listLives[i]?.liveId)
    //                 // if (dayOfMonth >= 20) {
    //                 //     goodlist.push(item)
    //                 //     console.log('有抽奖',item.liveId,item.activeCode);
    //                 //     goAllLottery([item])
    //                 // } else if (maxNumber >= 50) {
    //                 //     goodlist.push(item)
    //                 //     console.log('有抽奖',item.liveId,item.activeCode);
    //                 //     goAllLottery([item])
    //                 // }
    //             } else {
    //                 // console.log('没有抽奖', item);
    //                 item.liveId = listLives[i]?.liveId
    //             }
    //         })
    //     } else {
    //         console.log(data?.data);
    //         console.log('直播间商品列表返回和实际数量不一样');
    //     }
    // }
    let arr=listLives.map(async item=>{
        let data = await getGoodList(item.liveId, 1, token)
        if (data?.data?.list?.length == data?.data?.count) {
            // console.log('直播间商品列表返回和实际数量一样');
            data?.data?.list?.map(async ite => {
                if (ite.activeCode&&!runGameId.includes(ite.activeCode)) {
                    ite.liveId = item?.liveId
                    goodlist.push(ite)
                    console.log('有抽奖',ite.liveId,item.title,ite.activeCode);
                    goAllLottery([ite])
                    runGameId.push(ite.activeCode);
                }else if(ite.activeCode){
                    ite.liveId = item?.liveId
                    // console.log('已抽取抽奖，不运行',ite.liveId,item.title,ite.activeCode);
                } else {
                    // console.log('没有抽奖', item);
                    ite.liveId = item?.liveId
                }
            })
        } else {
            console.log(data?.data);
            console.log('直播间商品列表返回和实际数量不一样');
        }
    })
    await Promise.all(arr)
    const uniqueGoodlist = goodlist.reduce((acc, item) => {
        const key = `${item.liveId}-${item.activeCode}`;
        if (!acc.some(el => `${el.liveId}-${el.activeCode}` === key)) {
            acc.push(item);
        }
        return acc;
    }, []);

    return uniqueGoodlist
}
//去重
function fn2(tempArr) {
    let result = [];
    let obj = {};
    for (let i = 0; i < tempArr.length; i++) {
        if (!obj[tempArr[i].liveId]) {
            result.push(tempArr[i]);
            obj[tempArr[i].liveId] = true;
        };
    };
    return result;
};

async function getLiveList(phone, password,loginObj) {
    let userInfo = await tool.loginPhone(phone, password,loginObj)
    if (!userInfo) {
        getlive('init')
        return
    }
    let userCode = await getUsercode(userInfo.uid)
    let token = await getToken(userCode)
    await initFloor(1,1,1,token)
}
async function getlive(type) {
    if (type == 'init') {
        console.log('初始化');
        // 生成一个0到accounts.length-1之间的随机索引
        let randomIndex = Math.floor(Math.random() * userPhone.length);

        // 使用随机索引来获取随机账号
        let selectedAccount = userPhone[randomIndex];
        getLiveList(selectedAccount.phone, selectedAccount.password,selectedAccount.loginObj)
    } else {
        // 生成一个0到accounts.length-1之间的随机索引
        let randomIndex = Math.floor(Math.random() * userPhone.length);

        // 使用随机索引来获取随机账号
        let selectedAccount = userPhone[randomIndex];
        if (selectedAccount.xbkToken) {
            await initFloor(1,1,1,selectedAccount.xbkToken)

            // getGood()
        } else {
            getlive()
        }
    }
}
async function getGood() {
    try {
            // 生成一个0到accounts.length-1之间的随机索引
        let randomIndex = Math.floor(Math.random() * userPhone.length);

        // 使用随机索引来获取随机账号
        let selectedAccount = userPhone[randomIndex];
        // console.log(selectedAccount);
        if (selectedAccount.xbkToken) {
            await getStart(selectedAccount.xbkToken)
            // console.log('可抽奖数',goodList.length,'个');
            // if (goodList.length > 0) {
            //     console.log('有可抽奖活动', goodList.length,'个');
            //     goAllLottery()
            // } else {
            //     // console.log('没有可抽奖活动');
            // }
        } else {
            console.log('没有登录');
            getGood()
        }
    } catch (e) {
        getGood()
        console.log(e);
    }
}

let isStart=false

async function goAllLottery(goodLists) {
    try{
        isStart=true
        console.log('开始抽奖', goodLists[0].liveId, goodLists[0].activeCode)
        // for(let index=0;index<userPhone.length;index++){
        //     if (userPhone[index].xbkToken && userPhone[index].isDo) {
        //         for (let i = 0; i < goodLists.length; i++) {
        //             let number = await getLotteryChance(userPhone[index].xbkToken, goodLists[i].activeCode)
        //             if (number > 0) {
        //                 lotteryDo(goodLists[i].liveId, goodLists[i].activeCode, userPhone[index].xbkToken, userPhone[index].phone,userPhone[index].uid)
        //             }
        //         }
        //     }
        // }
        // await tool.wait(4000)
        let arr=userPhone.map(async item=>{
            if (item.xbkToken && item.isDo) {
                for (let i = 0; i < goodLists.length; i++) {
                    let number = await getLotteryChance(item.xbkToken, goodLists[i].activeCode)
                    for(let a=0;a<number;a++){
                        await lotteryDo(goodLists[i].liveId, goodLists[i].activeCode, item.xbkToken, item.phone,item.uid)
                        await tool.wait(4000)
                    }
                }
            }
        })
        await Promise.all(arr)
        
        console.log('开始准备推送',pushArr)
        for(let uid in pushArr){
            let str=''
            let number=0
            for(let phone in pushArr[uid]){
                str+=pushArr[uid][phone]
                let numberArr=extractNumbersWithDecimalsAndNegatives(pushArr[uid][phone])
                number+=numberArr[numberArr.length-1]
            }
            str+=`<div>本次抽奖收益：<span style="color: red;">${number}元话费</span></div>
            <div>需要付费金额：<span style="color: red;">${number/3}元</span></div>
            <img style="width: 70%;height: auto;" src="http://8.137.117.207:8888/down/e8WY1b1rJbWe.jpg" />
            <img style="width: 70%;height: auto;" src="http://8.137.117.207:8888/down/v9nqmTuDRunK.jpg" />`
            sendTxt[uid]=str
            console.log(str)
        }
        // console.log(pushArr)
        // console.log(sendTxt)
        pushArr={}
        isStart=false
    }catch(e){
        console.log(e);
        goAllLottery(goodLists)
    }
}
async function getUserAll() {
    
    
    try {
        Cache = JSON.parse(fs.readFileSync('./Cache.json', 'utf8'));
    } catch (error) {
        fs.writeFileSync('./Cache.json', JSON.stringify({}), 'utf8');
        Cache = JSON.parse(fs.readFileSync('./Cache.json', 'utf8'));
    }
    console.log('获取云端账号成功', userPhone.length)
    await allLogin()
}
//获取转盘的最大金额
async function prizeList(token, active_code, liveId) {
    try {
        const options = {
            method: "get",
            url: `https://xbk.189.cn/xbkapi/active/v2/lottery/prizeList?active_code=${active_code}&liveId=${liveId}&period=1`,
            headers: {
                'User-Agent': 'Mozilla/5.0 (Linux; U; Android 12; zh-cn; ONEPLUS A9000 Build/QKQ1.190716.003) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1',
                'Authorization': 'Bearer ' + rsaJiami.encrypt(token, 'base64')
            }
        };
        let res = await axios(options)
        let maxNumber = 0
        res?.data?.data?.map(item => {
            let arr = item.text.match(/\d+/g)
            if (arr && maxNumber < Number(arr[0])) {
                maxNumber = Number(arr[0])
            }
        })
        return maxNumber
    } catch (e) {
        return await prizeList(token, active_code, liveId)
    }
}
//获取可抽奖次数
async function getLotteryChance(token, active_code) {
    try {
        const options = {
            method: "get",
            url: "https://xbk.189.cn/xbkapi/active/v2/lottery/getLotteryChance?active_code=" + active_code,
            headers: {
                'User-Agent': 'Mozilla/5.0 (Linux; U; Android 12; zh-cn; ONEPLUS A9000 Build/QKQ1.190716.003) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1',
                'Authorization': 'Bearer ' + rsaJiami.encrypt(token, 'base64')
            }
        };
        let res = await axios(options)
        return res.data?.data
    } catch (e) {
        return 1
    }
}
//获取是否已抽中4次
async function getMyWinList(token) {
    return true
    try {
        const options = {
            method: "get",
            url: 'https://xbk.189.cn/xbkapi/active/v2/lottery/getMyWinList?page=1&give_status=200&activeCode=',
            headers: {
                'User-Agent': 'Mozilla/5.0 (Linux; U; Android 12; zh-cn; ONEPLUS A9000 Build/QKQ1.190716.003) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1',
                'Authorization': 'Bearer ' + rsaJiami.encrypt(token, 'base64')
            }
        };
        let res = await axios(options)
        let number = 0
        const currentDate = new Date();
        res?.data?.data?.map(item => {
            const winTime = new Date(item.win_time);
            const isSameMonth = winTime.getFullYear() === currentDate.getFullYear() &&
                winTime.getMonth() === currentDate.getMonth();
            if (isSameMonth && String(item.title).includes('话费')) {
                number += 1
            }
        })
        if (number >= 4) {
            return true
        } else {
            return true
        }
    } catch (e) {
        return true
    }
}
async function allLogin() {
    let arr=userPhone.map(async (item, index) => {
        if (!item.time) {
            let userInfo = await tool.loginPhoneTwo(item.phone, item.password,Cache)
            userPhone[index].time = new Date().valueOf()
            if (!userInfo) {
                userPhone[index].isLogin = false
                return
            }
            let userCode = await getUsercode(userInfo.uid)
            let token = await getToken(userCode)
            // console.log(token);
            userPhone[index].xbkToken = token
            userPhone[index].isDo = await getMyWinList(token)
            userPhone[index].isLogin = true
            if (!isGetLive&&liveListAll.length==0) {
                isGetLive = true
                await initFloor(1,1,1,token)
            }
        } else if (item.time && new Date().valueOf() - item.time > 1000 * 60 * 60 * 12) {
            let userInfo = await tool.loginPhoneTwo(item.phone, item.password,Cache)
            userPhone[index].time = new Date().valueOf()
            if (!userInfo) {
                userPhone[index].isLogin = false
                return
            }
            let userCode = await getUsercode(userInfo.uid)
            let token = await getToken(userCode)
            userPhone[index].xbkToken = token
            userPhone[index].isDo = await getMyWinList(token)
            userPhone[index].isLogin = true
        } else if (item.time && new Date().valueOf() - item.time > 1000 * 60 * 60 * 6 && !item.isLogin) {
            let userInfo = await tool.loginPhoneTwo(item.phone, item.password,Cache)
            userPhone[index].time = new Date().valueOf()
            if (!userInfo) {
                userPhone[index].isLogin = false
                return
            }
            let userCode = await getUsercode(userInfo.uid)
            let token = await getToken(userCode)
            userPhone[index].xbkToken = token
            userPhone[index].isDo = await getMyWinList(token)
            userPhone[index].isLogin = true
        }
    })
    await Promise.all(arr)
    // for (let index = 0; index < userPhone.length; index++) {
    //     if (!userPhone[index].time) {
    //         let userInfo = await loginPhone(userPhone[index].phone, userPhone[index].password)
    //         userPhone[index].time = new Date().valueOf()
    //         if (!userInfo) {
    //             userPhone[index].isLogin = false
    //             return
    //         }
    //         let userCode = await getUsercode(userInfo.uid)
    //         let token = await getToken(userCode)
    //         userPhone[index].xbkToken = token
    //         userPhone[index].isDo = await getMyWinList(token)
    //         userPhone[index].isLogin = true
    //         if (!isGetLive) {
    //             isGetLive = true
    //             await initFloor(1, 1, 2, token)
    //         }
    //     } else if (userPhone[index].time && new Date().valueOf() - userPhone[index].time > 1000 * 60 * 60 * 12) {
    //         let userInfo = await loginPhone(userPhone[index].phone, userPhone[index].password)
    //         userPhone[index].time = new Date().valueOf()
    //         if (!userInfo) {
    //             userPhone[index].isLogin = false
    //             return
    //         }
    //         let userCode = await getUsercode(userInfo.uid)
    //         let token = await getToken(userCode)
    //         userPhone[index].xbkToken = token
    //         userPhone[index].isDo = await getMyWinList(token)
    //         userPhone[index].isLogin = true
    //     } else if (userPhone[index].time && new Date().valueOf() - userPhone[index].time > 1000 * 60 * 60 * 6 && !userPhone[index].isLogin) {
    //         let userInfo = await loginPhone(userPhone[index].phone, userPhone[index].password)
    //         userPhone[index].time = new Date().valueOf()
    //         if (!userInfo) {
    //             userPhone[index].isLogin = false
    //             return
    //         }
    //         let userCode = await getUsercode(userInfo.uid)
    //         let token = await getToken(userCode)
    //         userPhone[index].xbkToken = token
    //         userPhone[index].isDo = await getMyWinList(token)
    //         userPhone[index].isLogin = true
    //     }
    // }
}

(async () => {
    getUserAll()
    try {
        liveListAll = JSON.parse(fs.readFileSync('./liveList.json', 'utf8'));
    } catch (error) {
        fs.writeFileSync('./liveList.json', JSON.stringify([]), 'utf8');
        liveListAll = JSON.parse(fs.readFileSync('./liveList.json', 'utf8'));
    }
    if(liveListAll.length==0){
        console.log('本地直播间为0,初始化加载直播间');
    }else{
        console.log('读取本地缓存直播间成功',liveListAll.length);
    }
})()
setInterval(async () => {
    console.log('更新直播间和账号列表');
    await getUserAll()
    getlive()
}, 1000 * 60 * 60)
setInterval(() => {
    getGood()
}, 1000 * 10)
setInterval(()=>{
    //10分钟清空一次红包抽奖，转盘抽奖。防止重复
    runGameId=[]
},1000*60*10)
setInterval(async ()=>{
    if(!isStart){
        let sendTxtlen=Object.keys(sendTxt)
        if(sendTxtlen.length > 0){
            for(let uid in sendTxt){
                await sendMsg(sendTxt[uid],uid)
                await tool.wait(3000)
            }
            sendTxt={}
        }
    }
},1000*60)