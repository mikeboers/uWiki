
function setup_ace_editor() {

    var $textarea = $('#content');
    var $editdiv = $('<div>').css({minHeight: '200px'}).insertBefore($textarea);
    $textarea.hide();

    var editor = ace.edit($editdiv[0]);
    editor.setTheme('ace/theme/tomorrow');
    
    var session = editor.getSession();
    session.setValue($textarea.val());
    session.setUseWrapMode(true);
    session.setWrapLimitRange(null, null);
    
    ace.config.setModuleUrl("mymarkdown", "/js/ace/mymarkdown.js");
    editor.getSession().setMode('ace/mode/markdown');

    editor.setOptions({
        maxLines: Infinity
    });

    var resize = function () {

        var newHeight =
            editor.getSession().getScreenLength()
            * editor.renderer.lineHeight
            + editor.renderer.scrollBar.getWidth();

        $editdiv.height(newHeight);
        editor.resize();

    }

    editor.on('change', resize);
    resize();

    $textarea.closest('form').submit(function() {
        $textarea.val(editor.getSession().getValue());
    });

}

function setup_mde_editor() {

    var $form = $('form#media-form');

    if ($form.data().mediaType == 'page') {
        var $textarea = $('#content');
        var editor = new SimpleMDE({element: $textarea[0]});
        $form.submit(function() {
            $textarea.val(editor.value());
        });
    }

}


app.endpoint_handler('media', function() {
    
    setup_mde_editor();

});
