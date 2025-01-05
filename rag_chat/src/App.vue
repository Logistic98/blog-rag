<template>
  <div class="app-container">
    <div :class="['chat', { 'mobile-no-border-radius': isMobile }]">
      <div :class="['chat_left', { 'chat_left_hidden': isMobile && !isLeftVisible }]">
        <div class="chat_left_head">
          <span>会话记录</span>
          <button v-if="isMobile" class="close-button" @click="toggleLeftVisible">✖</button>
        </div>
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
                class="record_input"
                @change="saveMessages"
              ></Input>
              <div class="button-group">
                <Button
                  shape="circle"
                  type="primary"
                  icon="md-create"
                  size="small"
                  class="edit-button"
                  v-if="!item.edit"
                  @click.stop="changeMessageEditStatus(item, true)"
                ></Button>
                <Button
                  shape="circle"
                  type="success"
                  icon="md-checkmark"
                  size="small"
                  class="save-button"
                  v-else
                  @click.stop="changeMessageEditStatus(item, false)"
                ></Button>
                <Button
                  shape="circle"
                  type="error"
                  icon="ios-trash"
                  size="small"
                  class="delete-button"
                  @click.stop="deleteRecord(index, item.id)"
                ></Button>
              </div>
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

      <div class="chat_right">
        <div class="chat_right_head_mobile" v-if="isMobile">
          <button class="menu-button" @click="toggleLeftVisible">☰</button>
          <div class="chat_right_head_title">
            {{ currentRecord.name }}
          </div>
        </div>
        <div class="chat_right_head" v-else>
          <div class="chat_title">{{ currentRecord.name }}</div>
        </div>
        <div class="chat_right_body" ref="messages">
          <div
            v-for="(message, index) in currentRecord.value"
            :key="'message' + index"
            :class="['message', { 'self': message.isSelf }]"
          >
            <img :src="message.avatar" class="avatar" />
            <div :class="['content', { 'self-content': message.isSelf }]">
              <div class="name">{{ message.name }}</div>
              <div v-if="message.isSelf">
                <div class="text markdown-body" v-html="message.text"></div>
              </div>
              <div v-else>
                <div v-if="message.step !== null && message.step < 4 && message.message" class="step-message">
                  第 {{ message.step }}/4 步：{{ message.message }}
                </div>
                <div v-else-if="message.step === 4 && !message.text" class="step-message">
                  第 {{ message.step }}/4 步：{{ message.message }}
                </div>
                <div v-if="message.step === 4 && message.text" class="render-switch">
                  <span class="render-label">渲染</span>
                  <i-switch v-model="message.isMarkdown" size="default"></i-switch>
                </div>
                <VueMarkdown
                  v-if="message.isMarkdown && message.text"
                  class="markdown markdown-body"
                  :source="message.text"
                ></VueMarkdown>
                <div class="text markdown-body" v-else-if="!message.isMarkdown && message.text" v-html="message.text"></div>
                <div v-if="message.loading && message.step === 0" class="log-loading">
                  <div class="dot"></div>
                  <div class="dot"></div>
                  <div class="dot"></div>
                </div>
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
        <div class="example-questions" ref="exampleContainer">
          <Button
            v-for="(example, index) in displayedExamples"
            :key="'example_' + index"
            class="example-button"
            @click="fillInput(example)"
          >
            {{ example }}
          </Button>
        </div>
        <div class="chat_right_send">
          <textarea
            class="chat_input_area"
            v-model="text"
            @keydown.enter.prevent="handleEnter"
            @compositionstart="isComposing = true"
            @compositionend="isComposing = false"
          ></textarea>
          <Button
            class="chat_input_button"
            :type="currentRecord.sending ? 'error' : 'success'"
            :icon="currentRecord.sending ? 'ios-close' : 'ios-send'"
            shape="circle"
            @click="currentRecord.sending ? stopGenerate() : sendMessage()"
          >
            {{ currentRecord.sending ? '停止' : '发送' }}
          </Button>
        </div>
      </div>
    </div>
    <div v-if="isMobile && isLeftVisible" class="overlay" @click="toggleLeftVisible"></div>
  </div>
</template>

<script>
import "github-markdown-css/github-markdown-light.css";
import VueMarkdown from 'vue-markdown';
import {API_URL, API_KEY, MODEL_NAME, DOC_URL_TEMPLATE, SERVER_NAME, USER_NAME, PROLOGUE, EXAMPLE_QUESTIONS} from './config';

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
        serverName: SERVER_NAME,
        userName: USER_NAME,
        prologue: PROLOGUE,
      },
      text: '',
      storageKey: 'chatInfo',
      abortController: null,
      isComposing: false,
      isLeftVisible: false,
      windowWidth: window.innerWidth,
      exampleQuestions: EXAMPLE_QUESTIONS,
      maxVisibleExamples: 1,
    };
  },
  computed: {
    isMobile() {
      return this.windowWidth <= 768;
    },
    displayedExamples() {
      if (this.isMobile) {
        return this.exampleQuestions.slice(0, this.maxVisibleExamples);
      }
      return this.exampleQuestions;
    }
  },
  mounted() {
    window.addEventListener('resize', this.handleResize);
    this.handleResize();

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

    if (!this.isMobile) {
      this.isLeftVisible = true;
    }

    this.$nextTick(() => {
      this.calculateMaxVisibleExamples();
    });

    this.setVh();
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize);
  },
  methods: {
    handleResize() {
      this.windowWidth = window.innerWidth;
      if (!this.isMobile) {
        this.isLeftVisible = true;
      }
      else {
        this.isLeftVisible = false;
      }
      this.$nextTick(() => {
        this.calculateMaxVisibleExamples();
      });
      this.setVh();
    },
    setVh() {
      let vh = window.innerHeight * 0.01;
      document.documentElement.style.setProperty('--vh', `${vh}px`);
    },
    toggleLeftVisible() {
      this.isLeftVisible = !this.isLeftVisible;
    },
    handleEnter() {
      if (!this.isComposing) {
        this.sendMessage();
      }
    },
    saveMessages() {
      window.localStorage.setItem(this.storageKey, JSON.stringify(this.messages));
    },
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
    changeMessageEditStatus(item, status) {
      item.edit = status;
    },
    recordCardClick(item) {
      this.currentRecord = item;
      this.currentId = item.id;
      if (this.isMobile) {
        this.isLeftVisible = false;
      }
    },
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
            isMarkdown: true,
            loading: false,
            step: 0,
            message: ''
          }
        ]
      };
      this.messages.push(newRecord);
      this.currentRecord = newRecord;
      this.currentId = newId;
      this.saveMessages();
    },
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
    formatReferences(references) {
      return references.map((docName, index) => {
        const title = docName;
        const url = DOC_URL_TEMPLATE.replace('{}', docName);
        return `<a href="${url}" target="_blank" rel="noopener noreferrer">[${index + 1}] ${title}</a>`;
      }).join('<br/>');
    },
    sendMessage() {
      if (
        !API_URL ||
        this.currentRecord.sending ||
        this.text.trim() === ''
      ) {
        return;
      }

      let userMessage = {
        id: this.messages.length + 1,
        name: this.options.userName,
        avatar: require('./assets/people.png'),
        text: this.text.trim(),
        isSelf: true,
        isMarkdown: false
      };
      this.currentRecord.value.push(userMessage);

      let assistantMessage = {
        id: this.messages.length + 1,
        name: this.options.serverName,
        avatar: require('./assets/robot.png'),
        text: '',
        isSelf: false,
        loading: true,
        isMarkdown: true,
        references: [],
        step: 0,
        message: ''
      };
      this.currentRecord.value.push(assistantMessage);

      let sendMsg = this.text.trim();
      this.text = '';
      this.currentRecord.sending = true;
      this.scrollToBottom();

      let sendData = {
        model: MODEL_NAME,
        messages: [{ role: 'user', content: sendMsg }],
        stream: true
      };

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
          assistantMessage.text = '抱歉，接口请求失败，请稍后再试。';
        }
        assistantMessage.loading = false;
        this.currentRecord.sending = false;
        this.saveMessages();
      });
    },
    fillInput(question) {
      this.text = question;
    },
    calculateMaxVisibleExamples() {
      if (!this.isMobile) {
        this.maxVisibleExamples = this.exampleQuestions.length;
        return;
      }

      this.$nextTick(() => {
        const container = this.$refs.exampleContainer;
        const buttons = container.querySelectorAll('.example-button');
        if (container && buttons.length > 0) {
          const containerWidth = container.clientWidth;
          const buttonStyles = getComputedStyle(buttons[0]);
          const buttonWidth = buttons[0].offsetWidth + parseInt(buttonStyles.marginRight);
          const max = Math.floor(containerWidth / buttonWidth);
          this.maxVisibleExamples = max > 0 ? max : 1;
        } else {
          this.maxVisibleExamples = 1;
        }
      });
    }
  }
};
</script>

<style scoped>
*, *::before, *::after {
  box-sizing: border-box;
}

.app-container {
  position: relative;
  width: 100%;
  height: calc(var(--vh, 1vh) * 100);
  background-color: rgb(223, 223, 227);
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

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
  width: 100%;
  max-width: 1300px;
  height: calc(var(--vh, 1vh) * 95);
  display: flex;
  flex-direction: row;
}

.chat_left {
  width: 280px;
  box-sizing: border-box;
  padding: 20px;
  background-color: #e7f8ff;
  display: flex;
  flex-direction: column;
  box-shadow: inset -2px 0 2px 0 rgba(0, 0, 0, 0.05);
  position: relative;
  transition: transform 0.3s ease;
  z-index: 1000;
}

.chat_left_hidden {
  transform: translateX(-100%);
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: 80%;
  max-width: 300px;
  box-shadow: 2px 0 5px rgba(0,0,0,0.3);
}

.chat_left_head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  font-size: 20px;
  font-weight: 700;
}

.close-button {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
}

.chat_left_body {
  flex: 1;
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
  height: 40px;
  cursor: pointer;
}

.chat_left_foot_button:hover {
  background-color: #f3f3f3;
}

.chat_right {
  flex: 1;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.chat_right_head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  flex: 0 0 70px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat_title {
  font-size: 20px;
  font-weight: bolder;
  margin: 0 auto;
  text-align: center;
}

.chat_right_head_mobile {
  display: none;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background-color: #fff;
  border-bottom: 1px solid #dedede;
  flex: 0 0 50px;
}

.chat_right_head_title {
  flex: 1;
  font-size: 18px;
  font-weight: bold;
  text-align: center;
}

.menu-button, .close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  margin-right: 10px;
}

.chat_right_body {
  flex: 1 1 auto;
  overflow-y: auto;
  padding: 20px;
  min-height: 100px;
}

.example-questions {
  flex: 0 0 auto;
  display: flex;
  flex-wrap: nowrap;
  overflow-x: auto;
  gap: 5px;
  padding: 10px 20px;
}

.example-button {
  background-color: #e0e0e0;
  border: none;
  border-radius: 20px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
  color: #000;
}

.example-button:hover {
  background-color: #d5d5d5;
}

.chat_right_send {
  flex: 0 0 auto;
  position: relative;
  padding: 10px 20px;
  box-sizing: border-box;
  border-top: 1px solid #dedede;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
  box-shadow: 0px -2px 4px rgba(0, 0, 0, 0.05);
  background-color: #fff;
}

.chat_input_area {
  width: 100%;
  border-radius: 10px;
  border: 1px solid #dedede;
  box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.03);
  background-color: white;
  color: black;
  font-family: inherit;
  resize: none;
  outline: none;
  overflow: hidden;
  padding: 8px 80px 8px 14px;
  height: 100px;
}

.chat_input_area:focus {
  border: 1px solid #1d93ab;
}

.chat_input_button {
  position: absolute;
  right: 25px;
  bottom: 25px;
  cursor: pointer;
}

.record_card {
  padding: 10px 14px;
  background-color: #fff;
  border-radius: 10px;
  margin-bottom: 10px;
  box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.05);
  transition: background-color 0.3s ease;
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
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  font-weight: bolder;
  margin-bottom: 5px;
}

.button-group {
  display: flex;
  gap: 5px;
}

.record_card_title span {
  flex: 1;
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
  height: 100%;
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

.content {
  margin-left: 10px;
}

.self-content {
  margin-right: 10px;
}

.text, .markdown {
  margin-top: 10px;
  font-size: 14px;
  text-align: left;
  border-radius: 10px;
  padding: 10px;
  max-width: 100%;
  word-wrap: break-word;
  word-break: break-all;
  border: 1px solid #dedede;
}

.log-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 20px;
  width: 60px;
  padding-left: 0;
  margin-top: 10px;
}

.log-loading .dot {
  width: 12px;
  height: 12px;
  margin: 0 4px;
  background-color: #07C160;
  border-radius: 50%;
  animation: dotFlashing 1s infinite ease-in-out;
  flex-shrink: 0;
}

@keyframes dotFlashing {
  0% { opacity: 1; }
  50% { opacity: 0.2; }
  100% { opacity: 1; }
}

.log-loading .dot:nth-child(1) {
  animation-delay: 0s;
}

.log-loading .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.log-loading .dot:nth-child(3) {
  animation-delay: 0.4s;
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
  max-width: 100%;
}

.render-switch {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-bottom: 5px;
}

.render-label {
  margin-right: 8px;
}

.markdown {
  margin-top: 10px;
  font-size: 14px;
  text-align: left;
  border-radius: 10px;
  padding: 10px;
  max-width: 100%;
  word-wrap: break-word;
  word-break: break-all;
  border: 1px solid #dedede;
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

@media (max-width: 768px) {
  .avatar {
    width: 35px;
    height: 35px;
  }

  .chat {
    flex-direction: column;
    border-radius: 0 !important;
    height: calc(var(--vh, 1vh) * 100);
  }

  .chat_left {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    width: 80%;
    max-width: 240px;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    box-shadow: 2px 0 5px rgba(0,0,0,0.3);
  }

  .chat_left_hidden {
    transform: translateX(-100%);
  }

  .chat_left:not(.chat_left_hidden) {
    transform: translateX(0);
  }

  .chat_right {
    width: 100%;
    display: flex;
    flex-direction: column;
    height: 100%;
  }

  .chat_right_head_mobile {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .chat_right_head {
    display: none;
  }

  .overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 900;
  }

  .chat_right_send {
    padding: 10px;
  }

  .chat_input_area {
    padding: 8px 20px 8px 14px;
    height: 50px;
    white-space: normal;
    text-overflow: unset;
    overflow: auto;
  }

  .record_card {
    padding: 8px 10px;
    font-size: 14px;
  }

  .chat_left {
    width: 240px;
    max-width: 240px;
  }

  .example-questions {
    padding: 10px 10px;
    gap: 10px;
  }

  .example-button {
    flex: 0 0 auto;
    margin-right: 10px;
  }

  .chat_right_head_title {
    text-align: center;
  }

  body, html, .app-container, .chat, .chat_left, .chat_right {
    overflow-x: hidden;
  }
}

@media (min-width: 769px) {
  .chat_input_area {
    height: 80px;
    min-height: 80px;
    white-space: pre-wrap;
    text-overflow: unset;
    padding: 8px 80px 8px 14px;
  }
}
</style>