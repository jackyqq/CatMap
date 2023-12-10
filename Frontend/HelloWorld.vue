<template>
  <div class="search-view">
    <h1>文献搜索引擎</h1>
    <div class="search-form">
      <input type="text" v-model="searchQuery" placeholder="请输入搜索内容..." class="search-input">
      <div class="criteria">
        <label><input type="checkbox" v-model="searchCriteria.title"> 标题</label>
        <label><input type="checkbox" v-model="searchCriteria.author"> 作者</label>
        <label><input type="checkbox" v-model="searchCriteria.keywords"> 关键词</label>
        <!-- 添加更多搜索字段 -->
      </div>
      <button @click="performSearch" class="search-button">搜索</button>
    </div>

    <div class="search-results" v-if="searchResults.length > 0">
      <div class="result-item" v-for="(item, index) in searchResults" :key="index">
        <h3>{{ item._source.title }}</h3>
        <p>{{ item._source.abstract }}</p>
        <!-- 根据需要展示更多信息 -->
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      searchQuery: '',
      searchCriteria: {
        title: false,
        author: false,
        keywords: false
        // 添加更多字段
      },
      searchResults: []
    };
  },
  methods: {
    performSearch() {
      const payload = {
        query: this.searchQuery,
        criteria: this.searchCriteria
      };
      this.$axios.post('http://localhost:8000/search', payload)
        .then(response => {
          this.searchResults = response.data.hits.hits;
        })
        .catch(error => {
          console.error("搜索请求错误:", error);
        });
    }
  }
};
</script>

<style>
.search-view {
  text-align: center;
}

.search-form {
  margin: 20px auto;
  width: 300px;
}

.search-input {
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.criteria {
  margin-bottom: 10px;
}

.search-button {
  width: 100%;
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search-button:hover {
  background-color: #0056b3;
}

.search-results {
  margin-top: 20px;
}

.result-item {
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
}

.result-item h3 {
  margin: 0 0 10px 0;
}

.result-item p {
  margin: 0;
  color: #666;
}
</style>

<!--
<template>
  <div class="homepage">
    <div class="search-box">
      <input type="text" v-model="searchQuery" placeholder="请输入搜索内容...">
      <button @click="performSearch">搜索</button>
      <button @click="performTestGet">测试 GET 请求</button>
    </div>

    <div class="response">
      <h3>响应结果：</h3>
      <pre>{{ responseResult }}</pre>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      searchQuery: '',
      responseResult: null
    };
  },
  methods: {
    performSearch() {
      this.responseResult = null;
      this.$axios.post('http://localhost:8000/search', { query: this.searchQuery })
        .then(response => {
          this.responseResult = response.data;
        })
        .catch(error => {
          console.error("搜索请求错误:", error);
          this.responseResult = '搜索请求失败';
        });
    },
    performTestGet() {
      this.responseResult = null;
      this.$axios.get('http://localhost:8000/test')
        .then(response => {
          this.responseResult = response.data;
        })
        .catch(error => {
          console.error("GET 请求错误:", error);
          this.responseResult = 'GET 请求失败';
        });
    }
  }
};
</script>

<style>
.homepage {
  text-align: center;
}

.search-box {
  margin: 20px;
}

.response {
  margin-top: 20px;
}

/* 可根据需要添加更多样式 */
</style>

-->
