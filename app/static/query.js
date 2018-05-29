$(function(){
    $('#query-form').on('submit', function(){
        var queryString = $('#searchInput').val(),
            enginetype = $('#enginetype').val();

        if (queryString != '') {
            $.ajax({
                url:'/query',
                type:'POST',
                dataType: 'json',
                data: {'queryString': queryString, 'enginetype': enginetype},
                beforeSend: function () {
                    $("#searchBtn").prop("disabled", true);
                },
                complete: function () {
                    $("#searchBtn").removeAttr("disabled");
                },
                success: function (data) {
                    if (data.result == "Success") {
                        $("#alert_div").hide();
                        $("#resultTextArea").val(data.text);
                    } else {
                        $("#alert_div").show();
                        $("#errorText").text("Sorry, the analysis failed. " + "Reason:" + data.message);
                    }

                },
                error: function () {
                    $("#alert_div").show();
                    $("#errorText").text("Sorry, the analysis failed.");
                }
            })
        }
        else
        {
            $("#alert_div").show();
            $("#errorText").text("Please enter a query.");
        }
        return false;
    })
})