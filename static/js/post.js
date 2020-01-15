$("button[name='btn_delete_post']").click(function () {

    var data = {post_id: $(this).data('post_id')}

    $.ajax({
        type: 'POST',
        url: "/delete_post",
        data: data,
        dataType: "text",
        success: function (resultData) {
            location.reload();
        }
    });
});


$("button[name='btn_edit_post']").click(function () {

    window.location = "edit_post?post_id=" + $(this).data('post_id');

});


$("button[name='btn_new_post']").click(function () {

    window.location = "new_post/" + $(this).data('group_id');

});




$("button[name='btn_view_hashtag']").click(function () {

    window.location = "http://127.0.0.1:5000/hashtag/" + $(this).data('post_id');

});

$("button[name='btn_new_hashtag']").click(function () {

    window.location = "new_hashtag/" + $(this).data('post_id');

});