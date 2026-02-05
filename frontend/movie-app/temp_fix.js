const addToWatchlist = async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  if (!movie.value) {
    ElMessage.warning('电影数据未加载')
    return
  }
  
  try {
    console.log('Adding to watchlist, movie ID:', movie.value?.id)
    const result = await watchlistStore.toggleWatchlist(movie.value.id)
    console.log('Add to watchlist result:', result)
    
    if (result.added) {
      ElMessage.success('已将《' + movie.value?.title + '》加入想看列表')
    } else {
      ElMessage.info('《' + movie.value?.title + '》已从想看列表中移除')
    }
  } catch (error: any) {
    console.error('Add to watchlist error:', error)
    ElMessage.error('操作失败，请重试')
  }
}