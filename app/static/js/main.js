(function ($) {
    "use strict";

    $(document).ready(function(){
        // Inicialize o campo de entrada com a máscara de dinheiro
        $('#vl_inicial').maskMoney({
            prefix: 'R$ ', 
            allowNegative: true, 
            thousands: '.', 
            decimal: ',', 
            affixesStay: false
        });
    
        // Adicione um evento de saída do campo de entrada para formatar o valor corretamente
        $('#vl_inicial').blur(function(){
            // Remova a máscara temporariamente para obter o valor sem formatação
            var unmasked_value = $(this).maskMoney('unmasked')[0];
            // Se o valor for numérico, formate-o com separadores de milhares e duas casas decimais no formato brasileiro
            if(!isNaN(unmasked_value)){
                var formatted_value = parseFloat(unmasked_value).toFixed(2).replace('.', ',').replace(/\d(?=(\d{3})+,)/g, '$&.');
                // Defina o valor formatado de volta no campo de entrada
                $(this).val('R$ ' + formatted_value);
            }
        });
    });

    /*==================================================================
    [ Focus input ]*/
    $('.input100').each(function(){
        $(this).on('blur', function(){
            if($(this).val().trim() != "") {
                $(this).addClass('has-val');
            }
            else {
                $(this).removeClass('has-val');
            }
        })    
    })
  
  
    /*==================================================================
    [ Validate ]*/
    var input = $('.validate-input .input100');

    $('.validate-form').on('submit',function(){
        var check = true;

        for(var i=0; i<input.length; i++) {
            if(validate(input[i]) == false){
                showValidate(input[i]);
                check=false;
            }
        }

        return check;
    });


    $('.validate-form .input100').each(function(){
        $(this).focus(function(){
           hideValidate(this);
        });
    });

    function validate (input) {
        if($(input).attr('type') == 'email' || $(input).attr('name') == 'email') {
            if($(input).val().trim().match(/^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{1,5}|[0-9]{1,3})(\]?)$/) == null) {
                return false;
            }
        }
        else {
            if($(input).val().trim() == ''){
                return false;
            }
        }
    }

    function showValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).addClass('alert-validate');
    }

    function hideValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).removeClass('alert-validate');
    }
    
    /*==================================================================
    [ Show pass ]*/
    var showPass = 0;
    $('.btn-show-pass').on('click', function(){
        if(showPass == 0) {
            $(this).next('input').attr('type','text');
            $(this).addClass('active');
            showPass = 1;
        }
        else {
            $(this).next('input').attr('type','password');
            $(this).removeClass('active');
            showPass = 0;
        }
        
    });

})(jQuery);
