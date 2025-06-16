/**
 * 文章点赞功能
 */

$(document).ready(function() {
    // 使用事件绑定，而不是内联onclick
    $('#like-button').on('click', function() {
        const url = $(this).data('url');
        const id = $(this).data('id');
        const likes = $(this).data('likes');
        validate_is_like(url, id, likes);
    });
});

// 点赞功能主函数
function validate_is_like(url, id, likes) {
    // 取出 LocalStorage 中的数据
    let storage = window.localStorage;
    const storage_str_data = storage.getItem("my_blog_data");
    let storage_json_data = JSON.parse(storage_str_data);
    // 若数据不存在，则创建空字典
    if (!storage_json_data) {
        storage_json_data = {};
    }
    // 检查当前文章是否已点赞。是则 status = true
    const status = check_status(storage_json_data, id);
    if (status) {
        layer.msg('已经点过赞了哟~');
        // 点过赞则立即退出函数
        return;
    } else {
        // 用 Jquery 找到点赞数量，并 +1
        $('span#likes_number').text(likes + 1).css('color', '#dc3545');
    }
    // 用 ajax 向后端发送 post 请求
    $.post(
        url,
        // post 只是为了做 csrf 校验，因此数据为空
        {},
        function(result) {
            if (result === 'success') {
                // 尝试修改点赞数据
                try {
                    storage_json_data[id] = true;
                } catch (e) {
                    window.localStorage.clear();
                }

                const d = JSON.stringify(storage_json_data);
                // 尝试存储点赞数据到 LocalStorage
                try {
                    storage.setItem("my_blog_data", d);
                } catch (e) {
                    // code 22 错误表示 LocalStorage 空间满了
                    if (e.code === 22) {
                        window.localStorage.clear();
                        storage.setItem("my_blog_data", d);
                    }
                }
            } else {
                layer.msg("与服务器通信失败..过一会儿再试试呗~");
            }
        }
    );
}

// 辅助点赞主函数，验证点赞状态
function check_status(data, id) {
    // 尝试查询点赞状态
    try {
        if (id in data && data[id]) {
            return true;
        } else {
            return false;
        }
    } catch (e) {
        window.localStorage.clear();
        return false;
    }
} 