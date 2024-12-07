<template>
  <div style="height: 100vh; display: flex; justify-content: center; align-items: center; background-color: rgb(223 223 227)">
    <div class="chat">
      <!-- 左侧聊天记录列表 -->
      <div class="chat_left">
        <div class="chat_left_head">聊天记录</div>
        <div class="chat_left_body">
          <div
            v-for="(item, index) in messages"
            :key="'record_card' + index"
            :class="item.id === currentId ? 'record_card card_choose' : 'record_card'"
            @click="recordCardClick(item)"
          >
            <div class="record_card_title">
              <span v-if="!item.edit">{{ item.name }}</span>
              <Input
                v-else
                v-model="item.name"
                placeholder="请输入名称"
                style="width: 150px"
                @change="saveMessages"
              ></Input>
              <Button
                shape="circle"
                type="primary"
                icon="md-create"
                size="small"
                style="position: absolute; top: 7px; right: 38px; height: 26px; width: 26px"
                v-if="!item.edit"
                @click.stop="changeMessageEditStatus(item, true)"
              ></Button>
              <Button
                shape="circle"
                type="success"
                icon="md-checkmark"
                size="small"
                style="position: absolute; top: 7px; right: 38px; height: 26px; width: 26px"
                v-else
                @click.stop="changeMessageEditStatus(item, false)"
              ></Button>
              <Button
                shape="circle"
                type="error"
                icon="ios-trash"
                size="small"
                style="position: absolute; top: 7px; right: 7px; height: 26px; width: 26px"
                @click.stop="deleteRecord(index, item.id)"
              ></Button>
            </div>
            <div class="record_card_info">
              <div>{{ item.value.length }} 条会话</div>
              <div>{{ item.time }}</div>
            </div>
          </div>
        </div>
        <div class="chat_left_foot">
          <Button icon="md-add" class="chat_left_foot_button" @click="addNewDialog('新的会话')">新的会话</Button>
        </div>
      </div>

      <!-- 右侧聊天窗口 -->
      <div class="chat_right">
        <div class="chat_right_head">
          <div style="line-height: 65px; font-size: 20px; font-weight: bolder;">{{ currentRecord.name }}</div>
          <div style="font-size: 12px; position: relative; top: -16px;" v-if="currentRecord.sending">正在生成回复...</div>
        </div>
        <div class="chat_right_body" ref="messages">
          <div
            v-for="(message, index) in currentRecord.value"
            :key="'message' + index"
            :class="message.isSelf ? 'message self' : 'message'"
          >
            <img :src="message.avatar" class="avatar" />
            <div :class="message.isSelf ? 'content self' : 'content'">
              <div class="name">{{ message.name }}</div>
              <!-- 用户消息 -->
              <div v-if="message.isSelf">
                <div class="text markdown-body" v-html="message.text"></div>
              </div>
              <!-- 机器人消息 -->
              <div v-else>
                <!-- 显示步骤提示信息 -->
                <div v-if="message.step !== null && message.step < 3 && message.message" class="step-message">
                  {{ message.message }}
                </div>
                <!-- 渲染切换 -->
                <div v-if="message.step === 3 && message.text" class="render-switch">
                  <span style="margin-right: 8px;">渲染</span>
                  <i-switch v-model="message.isMarkdown" size="default"></i-switch>
                </div>
                <!-- 显示消息内容 -->
                <VueMarkdown
                  v-if="message.isMarkdown && message.text"
                  class="markdown markdown-body"
                  :source="message.text"
                ></VueMarkdown>
                <div class="text markdown-body" v-else-if="!message.isMarkdown && message.text" v-html="message.text"></div>
                <!-- 加载动画 -->
                <div v-if="message.loading && message.step === 0" class="log-loading">
                  <div class="dot-flashing"></div>
                </div>
                <!-- 显示参考资料 -->
                <div v-if="message.references && message.references.length > 0" class="references">
                  <div class="reference-title">参考资料：</div>
                  <VueMarkdown
                    class="markdown markdown-body"
                    :source="formatReferences(message.references)"
                  ></VueMarkdown>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- 停止生成按钮 -->
        <Button shape="circle" style="position: absolute; bottom: 120px; right: 20px" @click="stopGenerate" v-show="currentRecord.sending" type="info">停止生成</Button>
        <div class="chat_right_send">
          <div>
            <textarea
              class="chat_input_area"
              v-model="text"
              @keydown.enter.prevent="handleEnter"
              @compositionstart="isComposing = true"
              @compositionend="isComposing = false"
            />
            <Button
              class="chat_input_button"
              type="success"
              shape="circle"
              icon="ios-send"
              @click="sendMessage"
              :disabled="currentRecord.sending"
            >
              发送
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import "github-markdown-css/github-markdown-light.css";
import VueMarkdown from 'vue-markdown';
import { API_URL, API_KEY, MODEL_NAME, DOC_URL_TEMPLATE } from './config';

export default {
  components: {
    VueMarkdown,
  },
  data() {
    return {
      messages: [],
      currentRecord: {},
      currentId: 0,
      options: {
        serverName: '机器人',
        userName: '我',
        prologue: '你好，请问有什么可以帮助您?',
        paramName: '输入'
      },
      text: '',
      storageKey: 'chatInfo',
      abortController: null,  // 控制停止输出
      isComposing: false, // 标识输入法状态
    };
  },
  mounted() {
    if (localStorage.getItem(this.storageKey) !== null) {
      this.messages = JSON.parse(localStorage.getItem(this.storageKey));
      this.messages.forEach(item => {
        item.edit = false;
        item.sending = false;
      });
      this.recordCardClick(this.messages[0]);
    } else {
      this.addNewDialog('新的会话');
    }
  },
  methods: {
    // 如果不在输入法状态，则直接发送消息
    handleEnter() {
      if (!this.isComposing) {
        this.sendMessage();
      }
    },
    // 保存消息到本地存储
    saveMessages() {
      window.localStorage.setItem(this.storageKey, JSON.stringify(this.messages));
    },
    // 删除会话记录
    deleteRecord(index, id) {
      this.messages.splice(index, 1);
      if (this.currentRecord.id === id) {
        if (this.messages.length >= index + 1) {
          this.currentRecord = this.messages[index];
        } else if (index > 0) {
          this.currentRecord = this.messages[index - 1];
        } else {
          this.addNewDialog('新的会话');
        }
      }
      this.saveMessages();
    },
    // 修改聊天记录编辑状态
    changeMessageEditStatus(item, status) {
      item.edit = status;
    },
    // 选择聊天记录
    recordCardClick(item) {
      this.currentRecord = item;
      this.currentId = item.id;
    },
    // 停止生成
    stopGenerate() {
      if (this.abortController) {
        this.abortController.abort();
        this.abortController = null;
      }
      let lastIndex = this.currentRecord.value.length - 1;
      if (lastIndex >= 0) {
        this.currentRecord.value[lastIndex].text = '已停止生成';
        this.currentRecord.value[lastIndex].loading = false;
        this.currentRecord.value[lastIndex].step = null;
        this.currentRecord.value[lastIndex].message = '';
      }
      this.currentRecord.sending = false;
      this.saveMessages();
    },
    // 新增聊天
    addNewDialog(title) {
      let unique = 0;
      const time = Date.now();
      const random = Math.floor(Math.random() * 1000000000);
      unique++;
      let newId = random + unique + String(time);
      let nowData = new Date();
      let nowTime =
        nowData.getFullYear() +
        '/' +
        (nowData.getMonth() + 1) +
        '/' +
        nowData.getDate() +
        ' ' +
        nowData.getHours() +
        ':' +
        nowData.getMinutes() +
        ':' +
        nowData.getSeconds();
      let newRecord = {
        id: newId,
        name: title,
        time: nowTime,
        edit: false,
        sending: false,
        value: [
          {
            id: this.messages.length + 1,
            name: this.options.serverName,
            avatar: require('./assets/robot.png'),
            text: this.options.prologue,
            isSelf: false,
            isMarkdown: false,
            loading: false,
            step: 0, // 初始化为0，表示正在加载
            message: '' // 初始化提示信息为空
          }
        ]
      };
      this.messages.push(newRecord);
      this.currentRecord = newRecord;
      this.currentId = newId;
      this.saveMessages();
    },
    // 滚动到底部
    scrollToBottom() {
      this.$nextTick(() => {
        let scrollElem = this.$refs.messages;
        if (scrollElem) {
          scrollElem.scrollTo({
            top: scrollElem.scrollHeight,
            behavior: 'smooth'
          });
        }
      });
    },
    // 格式化参考资料返回
    formatReferences(references) {
      return references.map((docName, index) => {
        const title = docName;
        const url = DOC_URL_TEMPLATE.replace('{}', docName);
        return `<a href="${url}" target="_blank" rel="noopener noreferrer">[${index + 1}] ${title}</a>`;
      }).join('<br/>');
    },
    // 发送消息
    sendMessage() {
      // 检查必要条件
      if (
        !API_URL ||
        this.currentRecord.sending ||
        this.text.trim() === ''
      ) {
        return;
      }

      // 添加用户消息到对话
      let userMessage = {
        id: this.messages.length + 1,
        name: this.options.userName,
        avatar: require('./assets/people.png'),
        text: this.text.trim(),
        isSelf: true,
        isMarkdown: false
      };
      this.currentRecord.value.push(userMessage);

      // 准备机器人回复
      let assistantMessage = {
        id: this.messages.length + 1,
        name: this.options.serverName,
        avatar: require('./assets/robot.png'),
        text: '',
        isSelf: false,
        loading: true,
        isMarkdown: true,
        references: [], // 存储参考资料
        step: 0, // 当前步骤，初始化为0
        message: '' // 当前步骤的提示信息
      };
      this.currentRecord.value.push(assistantMessage);

      // 清空输入框并设置发送状态
      let sendMsg = this.text.trim();
      this.text = '';
      this.currentRecord.sending = true;
      this.scrollToBottom();

      // 准备请求数据
      let sendData = {
        model: MODEL_NAME,
        messages: [{ role: 'user', content: sendMsg }],
        stream: true
      };

      // 发送请求，处理流式响应
      this.abortController = new AbortController();
      fetch(API_URL, {
        method: 'POST',
        mode: 'cors',
        body: JSON.stringify(sendData),
        headers: {
          Authorization: 'Bearer ' + API_KEY,
          'Content-Type': 'application/json'
        },
        signal: this.abortController.signal
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('网络响应不正常');
        }
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let dataBuffer = '';

        const readStream = () => {
          reader.read().then(({ done, value }) => {
            if (done) {
              assistantMessage.loading = false;
              this.currentRecord.sending = false;
              this.saveMessages();
              return;
            }

            try {
              dataBuffer += decoder.decode(value, { stream: true });
              let lines = dataBuffer.split('\n');
              if (!dataBuffer.endsWith('\n')) {
                dataBuffer = lines.pop();
              } else {
                dataBuffer = '';
              }

              for (let line of lines) {
                line = line.trim();
                if (line.startsWith('data: ')) {
                  let jsonStr = line.substring(6).trim();
                  if (jsonStr === '[DONE]') {
                    assistantMessage.loading = false;
                    this.currentRecord.sending = false;
                    this.saveMessages();
                    return;
                  }
                  let data = JSON.parse(jsonStr);
                  let delta = data.choices[0].delta;

                  if (delta.step !== undefined && delta.message !== undefined) {
                    assistantMessage.step = delta.step;
                    assistantMessage.message = delta.message;
                  }
                  if (delta.content) {
                    if (!assistantMessage.text) {
                      this.$set(assistantMessage, 'text', '');
                    }
                    assistantMessage.text += delta.content;
                  }
                  if (delta.reference && delta.reference.length > 0) {
                    assistantMessage.references.push(...delta.reference);
                  }
                  this.$forceUpdate();
                  this.scrollToBottom();
                }
              }
              readStream();
            } catch (error) {
              if (error.name === 'AbortError') {
                console.log('读取流被中止');
              } else {
                console.error('解析错误:', error);
              }
            }
          }).catch(error => {
            if (error.name === 'AbortError') {
              console.log('请求已终止');
            } else {
              console.error('读取流错误:', error);
            }
          });
        };
        readStream();
      })
      .catch(error => {
        if (error.name === 'AbortError') {
          console.log('请求已终止');
        } else {
          console.error('请求错误:', error);
          assistantMessage.text = '抱歉，发生了一个错误。请稍后再试。';
        }
        assistantMessage.loading = false;
        this.currentRecord.sending = false;
        this.saveMessages();
      });
    }
  }
};
</script>

<style scoped>

::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}

::-webkit-scrollbar-thumb {
  background-color: #b2b2b2;
  border-radius: 32px;
}

::-webkit-scrollbar-track {
  background-color: #dbeffd;
  border-radius: 32px;
}

.card_choose {
  border: 2px solid #1d93ab !important;
}

.chat {
  background-color: #F4F4F4;
  border-radius: 20px;
  box-shadow: 0 0 20px rgba(128, 128, 128, 1);
  overflow: hidden;
  text-align: left;
  width: 1300px;
  height: 95%;
}

.chat_left {
  float: left;
  height: 100%;
  top: 0;
  width: 280px;
  box-sizing: border-box;
  padding: 20px;
  background-color: #e7f8ff;
  display: flex;
  flex-direction: column;
  box-shadow: inset -2px 0 2px 0 rgba(0, 0, 0, .05);
  position: relative;
  transition: width .05s ease;
}

.chat_left_head {
  position: relative;
  padding-top: 20px;
  padding-bottom: 20px;
  font-size: 20px;
  font-weight: 700;
}

.chat_left_body {
  flex: 1 1;
  overflow: auto;
  overflow-x: hidden;
}

.chat_left_foot {
  padding-top: 20px;
}

.chat_left_foot_button {
  background-color: #fff;
  border-radius: 20px;
  outline: none;
  border: none;
  color: #303030;
  float: right;
  height: 40px;
}

.chat_left_foot_button:hover {
  background-color: #f3f3f3;
}

.chat_right {
  float: left;
  width: calc(100% - 300px);
  background-color: #fff;
  display: flex;
  height: 100%;
  flex-direction: column;
  position: relative;
}

.chat_right_body {
  flex: 1 1;
  overflow: auto;
  padding: 20px 20px 40px;
  position: relative;
  overscroll-behavior: none;
}

.chat_right_send {
  position: relative;
  width: 100%;
  padding: 10px 20px 20px;
  box-sizing: border-box;
  flex-direction: column;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
  border-top: 1px solid #dedede;
  box-shadow: 0px 2px 4px 0px rgba(0, 0, 0, .05);
}

.chat_right_head {
  border-bottom: 1px solid rgba(0, 0, 0, .1);
  position: relative;
  justify-content: space-between;
  align-items: center;
  text-align: center;
  height: 70px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat_input_action {
  position: absolute;
  top: 30px;
  left: 10px;
}

.chat_input_area {
  height: 80px;
  width: 100%;
  margin-left: 5px;
  border-radius: 10px;
  border: 1px solid #dedede;
  box-shadow: 0 -2px 5px rgba(0, 0, 0, .03);
  background-color: white;
  color: black;
  font-family: inherit;
  padding: 10px 90px 10px 14px;
  resize: none;
  outline: none;
}

.chat_input_area:focus {
  border: 1px solid #1d93ab;
}

.chat_input_button {
  position: absolute;
  right: 30px;
  bottom: 32px;
}

.record_card {
  padding: 10px 14px;
  background-color: #fff;
  border-radius: 10px;
  margin-bottom: 10px;
  box-shadow: 0px 2px 4px 0px rgba(0, 0, 0, .05);
  transition: background-color .3s ease;
  cursor: pointer;
  user-select: none;
  border: 2px solid transparent;
  position: relative;
}

.record_card:hover {
  background-color: #f3f3f3;
}

.record_card_selected {
  border-color: #1d93ab;
}

.record_card_title {
  font-size: 14px;
  font-weight: bolder;
  display: block;
  width: 200px;
  height: 32px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.record_card_info {
  display: flex;
  justify-content: space-between;
  color: #a6a6a6;
  font-size: 12px;
}

.messages {
  height: 84%;
  overflow-y: auto;
}

.message {
  display: flex;
  margin: 10px 20px;
  padding: 10px;
}

.message.self {
  flex-direction: row-reverse;
}

.avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
}

.name {
  font-size: 14px;
  font-weight: bold;
}

.text {
  margin-top: 10px;
  font-size: 14px;
  text-align: left;
  border-radius: 10px;
  padding: 10px;
  max-width: 600px;
  word-wrap: break-word;
  word-break: break-all;
  white-space: pre-wrap;
  border: 1px solid #dedede;
}

.markdown {
  margin-top: 10px;
  font-size: 14px;
  text-align: left;
  border-radius: 10px;
  padding: 10px;
  max-width: 600px;
  word-wrap: break-word;
  word-break: break-all;
  border: 1px solid #dedede;
}

.log-loading {
  height: 20px;
  width: 45px;
  padding-left: 20px;
  margin-top: 10px;
}

.dot-flashing {
  position: relative;
  width: 10px;
  height: 10px;
  border-radius: 5px;
  background-color: #07C160;
  color: #07C160;
  animation: dotFlashing 1s infinite linear alternate;
  animation-delay: .5s;
}

.references {
  margin-top: 10px;
  padding: 10px;
  background-color: #f9f9f9;
  border-left: 4px solid #1d93ab;
  border-radius: 5px;
}

.reference-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.references ul {
  list-style-type: disc;
  margin-left: 20px;
}

.references li a {
  color: #0969da;
  text-decoration: none;
}

.references li a:hover {
  text-decoration: underline;
}

.step-message {
  margin-top: 10px;
  font-size: 14px;
  color: #1d93ab;
  padding: 10px;
  background-color: #e7f8ff;
  border-radius: 5px;
  max-width: 600px;
}

.render-switch {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-bottom: 5px;
}

.markdown-body {
  box-sizing: border-box;
  min-height: 20px;
  min-width: 200px;
  max-width: 750px;
  margin: 0 auto;
  padding: 15px;
}

.markdown-body, [data-theme="light"] {
  --color-prettylights-syntax-comment: #6e7781;
  --color-prettylights-syntax-constant: #0550ae;
  --color-prettylights-syntax-entity: #6639ba;
  --color-prettylights-syntax-storage-modifier-import: #24292f;
  --color-prettylights-syntax-entity-tag: #116329;
  --color-prettylights-syntax-keyword: #cf222e;
  --color-prettylights-syntax-string: #0a3069;
  --color-prettylights-syntax-variable: #953800;
  --color-prettylights-syntax-brackethighlighter-unmatched: #82071e;
  --color-prettylights-syntax-invalid-illegal-text: #f6f8fa;
  --color-prettylights-syntax-invalid-illegal-bg: #82071e;
  --color-prettylights-syntax-carriage-return-text: #f6f8fa;
  --color-prettylights-syntax-carriage-return-bg: #cf222e;
  --color-prettylights-syntax-string-regexp: #116329;
  --color-prettylights-syntax-markup-list: #3b2300;
  --color-prettylights-syntax-markup-heading: #0550ae;
  --color-prettylights-syntax-markup-italic: #24292f;
  --color-prettylights-syntax-markup-bold: #24292f;
  --color-prettylights-syntax-markup-deleted-text: #82071e;
  --color-prettylights-syntax-markup-deleted-bg: #ffebe9;
  --color-prettylights-syntax-markup-inserted-text: #116329;
  --color-prettylights-syntax-markup-inserted-bg: #dafbe1;
  --color-prettylights-syntax-markup-changed-text: #953800;
  --color-prettylights-syntax-markup-changed-bg: #ffd8b5;
  --color-prettylights-syntax-markup-ignored-text: #eaeef2;
  --color-prettylights-syntax-markup-ignored-bg: #0550ae;
  --color-prettylights-syntax-meta-diff-range: #8250df;
  --color-prettylights-syntax-brackethighlighter-angle: #57606a;
  --color-prettylights-syntax-sublimelinter-gutter-mark: #8c959f;
  --color-prettylights-syntax-constant-other-reference-link: #0a3069;
  --color-fg-default: #1F2328;
  --color-fg-muted: #656d76;
  --color-fg-subtle: #6e7781;
  --color-canvas-default: #ffffff;
  --color-canvas-subtle: #f6f8fa;
  --color-border-default: #d0d7de;
  --color-border-muted: hsla(210,18%,87%,1);
  --color-neutral-muted: rgba(175,184,193,0.2);
  --color-accent-fg: #0969da;
  --color-accent-emphasis: #0969da;
  --color-attention-fg: #9a6700;
  --color-attention-subtle: #fff8c5;
  --color-danger-fg: #d1242f;
  --color-done-fg: #8250df;
}

@keyframes dotFlashing {
  0% {
    background-color: #07C160;
  }
  50% {
    background-color: #07C160;
  }
  100% {
    background-color: transparent;
  }
}

</style>
