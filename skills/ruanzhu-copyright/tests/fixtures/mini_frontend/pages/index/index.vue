<template>
  <view class="page">
    <text>{{ title }}</text>
  </view>
</template>

<script>
export default {
  data() {
    return { title: '首页' };
  },
  methods: {
    goOrder() {
      uni.navigateTo({ url: '/pages/order/list' });
    }
  }
};
</script>

<style scoped lang="scss">
.page {
  background: #fff;
  /* 这段 style 必须被程序鉴别材料脚本剔除 */
  padding: 20rpx;
}
</style>
