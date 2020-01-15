$("button[name='btn_delete_person']").click(function() {

    var data = { person_login : $(this).data('person_login')}

    $.ajax({
      type: 'POST',
      url: "/delete_person",
      data: data,
      dataType: "text",
      success: function(resultData) {
          location.reload();
      }
});
});


$("button[name='btn_edit_person']").click(function() {

    window.location = "edit_person?person_login="+$(this).data('person_login');

});


$("button[name='btn_new_person']").click(function() {

    window.location = "new_person";

});

$("button[name='btn_new_function']").click(function() {

    window.location = "new_function/"+$(this).data('person_login');

});

$("button[name='btn_ban']").click(function() {

    window.location = "ban/"+$(this).data('person_login');

});



$("button[name='btn_unban']").click(function() {

    window.location = "unban/"+$(this).data('person_login');

});
