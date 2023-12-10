<template>
  <div id="app">
    <!-- 页头 -->
    <header>
      <h1>catmap搜索引擎</h1>
    </header>

    <!-- 导航栏 -->
    <nav>
      <ul>
        <li><router-link to="/">主页</router-link></li>
        <li><router-link to="/news">新闻</router-link></li>
        <li><router-link to="/images">图片</router-link></li>
        <!-- 更多导航项... -->
      </ul>
    </nav>

    <!-- 路由视图 -->
    <router-view></router-view>

    <!-- 页脚 -->
    <footer>
      <p>版权所有 &copy; 2023 catmap搜索引擎</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
};
</script>

<style>
/* 添加一些基础样式 */
#app {
  text-align: center;
}

header {
  background-color: #f2f2f2;
  padding: 20px;
  margin-bottom: 15px;
}

nav ul {
  list-style-type: none;
  padding: 0;
  overflow: hidden;
  background-color: #333;
}

nav ul li {
  float: left;
}

nav ul li a {
  display: block;
  color: white;
  text-align: center;
  padding: 14px 16px;
  text-decoration: none;
}

nav ul li a:hover {
  background-color: #111;
}

footer {
  background-color: #f2f2f2;
  padding: 10px;
  position: fixed;
  left: 0;
  bottom: 0;
  width: 100%;
  text-align: center;
}
</style>
