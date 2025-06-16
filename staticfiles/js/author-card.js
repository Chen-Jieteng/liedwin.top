/**
 * 作者名片功能 - 实现鼠标悬停在作者头像上时显示详细信息
 */
$(document).ready(function() {
    // 全局变量，用于跟踪当前打开的popover
    let currentPopover = null;
    let popoverTimeout = null;
    
    // 初始化作者名片popover
    $('.author-popover').popover({
        container: 'body',
        html: true,
        trigger: 'manual', // 改为手动触发，以便我们控制显示/隐藏行为
        template: '<div class="popover author-card-popover" role="tooltip"><div class="arrow"></div><div class="popover-body p-0"></div></div>',
        content: function() {
            const authorId = $(this).data('author-id');
            const authorName = $(this).data('author-name');
            const authorAvatar = $(this).data('author-avatar');
            const authorBio = $(this).data('author-bio');
            
            // 创建基础卡片内容
            let cardContent = `
                <div class="author-card">
                    <div class="card-header">
                        <div class="author-info">
                            <div class="author-avatar-lg ${authorAvatar ? '' : 'bg-light d-flex align-items-center justify-content-center'}">
                                ${authorAvatar 
                                    ? `<img src="${authorAvatar}" alt="${authorName}">` 
                                    : `<i class="fas fa-user fa-2x text-secondary"></i>`
                                }
                            </div>
                            <div>
                                <div class="author-name">${authorName}</div>
                                <div class="small text-muted">${authorBio}</div>
                            </div>
                        </div>
                    </div>
                    <div class="author-stats" id="author-stats-${authorId}">
                        <div class="stat-item">
                            <div class="stat-value"><i class="fas fa-spinner fa-spin"></i></div>
                            <div class="stat-label">文章</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value"><i class="fas fa-spinner fa-spin"></i></div>
                            <div class="stat-label">粉丝</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value"><i class="fas fa-spinner fa-spin"></i></div>
                            <div class="stat-label">关注</div>
                        </div>
                    </div>
                    <!-- 暂时注释掉访问主页按钮
                    <div class="card-footer">
                        <a href="/user/${authorId}" class="btn btn-sm btn-primary btn-follow w-100">访问主页</a>
                    </div>
                    -->
                </div>
            `;
            
            // 在返回卡片内容的同时，触发AJAX请求获取实时数据
            setTimeout(() => {
                fetchAuthorStats(authorId);
            }, 50);
            
            return cardContent;
        }
    });
    
    // 显示popover的函数
    function showPopover(element) {
        // 如果有其他打开的popover，先关闭
        if (currentPopover && currentPopover[0] !== element[0]) {
            currentPopover.popover('hide');
        }
        
        element.popover('show');
        currentPopover = element;
        
        // 在新显示的popover上添加鼠标事件
        $('.author-card-popover').on('mouseenter', function() {
            clearTimeout(popoverTimeout);
        }).on('mouseleave', function() {
            popoverTimeout = setTimeout(function() {
                if (currentPopover) {
                    currentPopover.popover('hide');
                    currentPopover = null;
                }
            }, 300);
        });
    }
    
    // 鼠标进入作者头像
    $('.author-popover').on('mouseenter', function() {
        const $this = $(this);
        clearTimeout(popoverTimeout);
        showPopover($this);
    });
    
    // 鼠标离开作者头像
    $('.author-popover').on('mouseleave', function() {
        const $this = $(this);
        
        // 设置延迟，给用户时间将鼠标移到popover上
        popoverTimeout = setTimeout(function() {
            // 检查鼠标是否在popover上
            if (!$('.author-card-popover:hover').length) {
                $this.popover('hide');
                currentPopover = null;
            }
        }, 300);
    });
    
    // 点击页面其他区域关闭popover
    $(document).on('click', function(e) {
        if (currentPopover && 
            !$(e.target).closest('.author-popover').length && 
            !$(e.target).closest('.author-card-popover').length) {
            currentPopover.popover('hide');
            currentPopover = null;
        }
    });
    
    // 处理移动设备 - 点击代替悬停
    if (window.innerWidth < 768) {
        $('.author-popover').off('mouseenter mouseleave');
        
        $('.author-popover').on('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const $this = $(this);
            
            if (currentPopover && currentPopover[0] === $this[0]) {
                // 如果点击的是当前打开的popover触发元素，则关闭它
                $this.popover('hide');
                currentPopover = null;
            } else {
                // 否则显示此popover
                showPopover($this);
                
                // 移动设备下的内容
                const authorId = $this.data('author-id');
                setTimeout(() => {
                    fetchAuthorStats(authorId, true);
                }, 50);
            }
        });
    }
    
    // 获取作者统计信息的函数
    function fetchAuthorStats(authorId, isMobile = false) {
        $.ajax({
            url: `/api/user/${authorId}/stats/`,
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                // 确定目标元素ID
                const targetId = isMobile ? `#author-stats-mobile-${authorId}` : `#author-stats-${authorId}`;
                
                // 更新统计数据
                const statsContainer = $(targetId);
                if (statsContainer.length) {
                    const statItems = statsContainer.find('.stat-item');
                    
                    // 更新文章数
                    $(statItems[0]).find('.stat-value').html(data.article_count);
                    
                    // 更新粉丝数
                    $(statItems[1]).find('.stat-value').html(data.follower_count);
                    
                    // 更新关注数
                    $(statItems[2]).find('.stat-value').html(data.following_count);
                }
            },
            error: function() {
                // 错误处理 - 显示默认值或错误消息
                const targetId = isMobile ? `#author-stats-mobile-${authorId}` : `#author-stats-${authorId}`;
                const statsContainer = $(targetId);
                
                if (statsContainer.length) {
                    const statItems = statsContainer.find('.stat-item');
                    $(statItems[0]).find('.stat-value').html('0');
                    $(statItems[1]).find('.stat-value').html('0');
                    $(statItems[2]).find('.stat-value').html('0');
                }
            }
        });
    }
    
    // 确保智能客服引导提示正常工作
    $(document).on('DOMContentLoaded', function() {
        // 获取智能客服相关元素
        const tooltip = document.getElementById('aiGuideTooltip');
        const closeTooltip = document.getElementById('closeTooltip');
        const chatToggleBtn = document.getElementById('chatToggleBtn');
        const chatContainer = document.getElementById('chatContainer');
        
        if (tooltip && closeTooltip && chatToggleBtn) {
            // 显示智能客服引导
            setTimeout(function() {
                tooltip.classList.add('show');
                
                // 让智能客服按钮呼吸闪烁
                chatToggleBtn.classList.add('pulse-animation');
                
                // 动画结束后停止
                setTimeout(function() {
                    chatToggleBtn.classList.remove('pulse-animation');
                }, 4500); // 1.5s × 3次
                
                // 30秒后自动隐藏提示
                setTimeout(function() {
                    tooltip.classList.remove('show');
                }, 30000);
            }, 2000);
            
            // 关闭提示
            closeTooltip.addEventListener('click', function() {
                tooltip.classList.remove('show');
            });
            
            // 点击智能客服按钮时也隐藏提示
            chatToggleBtn.addEventListener('click', function() {
                tooltip.classList.remove('show');
                chatContainer.classList.toggle('active');
            });
        }
    });
}); 