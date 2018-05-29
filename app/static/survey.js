$(function () {
    var objScore = {};
    var len = $('textarea').length;
    $('input[type="radio"]').on('click', function () {
        var name = $(this).attr('name');
        var val = $(this).val();
        objScore[name] = val;
        if(Object.getOwnPropertyNames(objScore).length === len){
            $('#submit_svy').attr('disabled',false);
        }
    });


    $('#submit_svy').on('click', function () {
        var commtens = '';
        $('textarea').each(function (i, o) {
            commtens += encodeURIComponent($(o).val()) + '|||'
        });

        if (commtens.length > 3) {
            commtens = commtens.substring(0, commtens.length - 3);
        }

        var arrScore=[];
        for(var prop in objScore){
            if(objScore.hasOwnProperty(prop)){
                arrScore.push(objScore[prop]);
            }
        }

        var data = {
            score: arrScore.join('|||'),
            comments: commtens
        };
        var id = $('#svy_id').val();
        $.ajax({
            type: "POST",
            url: "/survey/completed/" + id,
            data: data,
            dataType: "json",
            success: function (data) {
                if (data['result'] === 'Success') {
                    document.location ='/survey/survey_completed_succ';
                } else {
                    alert("Error!");
                }
            }
        });
    });
});