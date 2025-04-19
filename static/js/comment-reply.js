/**
 * 评论回复功能
 */

$(document).ready(function() {
    // 为所有回复按钮添加事件监听
    $('.reply-btn').on('click', function() {
        const articleId = $(this).data('article-id');
        const commentId = $(this).data('comment-id');
        load_modal(articleId, commentId);
    });
});

// 加载回复模态框
function load_modal(article_id, comment_id) {
    let modal_body = '#modal_body_' + comment_id;
    let modal_id = '#comment_' + comment_id;

    // 加载编辑器
    if ($(modal_body).children().length === 0) {
        let content = '<iframe src="/comment/post-comment/' +
            article_id +
            '/' +
            comment_id +
            '" frameborder="0" style="width: 100%; height: 100%;"></iframe>';
        $(modal_body).append(content);
    }

    $(modal_id).modal('show');
}

// 处理二级回复
function post_reply_and_show_it(new_comment_id, article_id) {
    let next_url = "/article/article-detail/" + article_id + "/";
    // 去除 url 尾部 '/' 符号
    next_url = next_url.charAt(next_url.length - 1) == '/' ? next_url.slice(0, -1) : next_url;
    // 刷新并定位到锚点
    window.location.replace(next_url + "#comment_elem_" + new_comment_id);
} 