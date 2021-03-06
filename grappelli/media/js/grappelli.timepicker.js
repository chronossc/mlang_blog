(function( $ ) {


$.widget("ui.timepicker", {
    // default options
    options: {
        template: '<div id="ui-timepicker" class="module" style="position: absolute; display: none;"></div>',
        timepicker_selector: "#ui-timepicker",
        offset: {
            top: 0
        },
        time_list: [
            'now',
            '00:00',
            '01:00',
            '02:00',
            '03:00',
            '04:00',
            '05:00',
            '06:00',
            '07:00',
            '08:00',
            '09:00',
            '10:00',
            '11:00',
            '12:00',
            '13:00',
            '14:00',
            '15:00',
            '16:00',
            '17:00',
            '18:00',
            '19:00',
            '20:00',
            '21:00',
            '22:00',
            '23:00'
        ]
    },
    
    _create: function() {
        //console.log("JO!", this.element)
        //this.element.after('<button type="button" class="ui-timepicker-trigger"></button>');
        //this.element.next().click(function() {
        //    alert("JOJO!!!")
        //});
        var self = this,
            options = self.options;
        
        this._init();
        
        this.element.addClass("hasTimepicker");
        this.button = $('<button type="button" class="ui-timepicker-trigger"></button>');
        this.element.after(this.button);
        
        // get/create timepicker
        this.timepicker = $(options.timepicker_selector);
        this.timepicker.hide();
        
        if (this.element.attr("disabled")) {
            this.button.attr("disabled", true);
        } else {
            // register events
            this.button.click(function() {
                self._toggleTimepicker();
            });
        }
        
        //this.element.focus(function() {
        //    self._toggleTimepicker();
        //})
    },
    
    _init: function() {
        if ($(this.options.timepicker_selector).size() > 0) return;
        
        var self = this,
            options = self.options,
            template = $(options.template),
            template_str = "<ul>";
            
        
        for (var i = 0; i < options.time_list.length; i++) {
            if (options.time_list[i] == "now") {
                template_str += '<li class="ui-state-active row">' + options.time_list[i] + '</li>';
            } else {
                template_str += '<li class="ui-state-default row">' + options.time_list[i] + '</li>';
            }
        }
        template_str += "</ul>";
        template.append(template_str);
        
        template.appendTo("body").find('li').click(function() {
            $(this).parent().children('li').removeClass("ui-state-active");
            $(this).addClass("ui-state-active");
            var new_val = $(this).html();
            if (new_val == "now") {
                var now = new Date(),
                    hours = now.getHours(), 
                    minutes = now.getMinutes();
                
                hours = ((hours < 10) ? "0" + hours : hours);
                minutes = ((minutes < 10) ? "0" + minutes : minutes);
                
                new_val = hours + ":" + minutes;
            }
            $(self.timepicker.data("current_input")).val(new_val);
            self.timepicker.hide();
        });
        
        $(document).mousedown(function(evt) {
            if (self.timepicker.is(":visible")) {
                var $target = $(evt.target);
                if ($target[0].id != self.timepicker[0].id && $target.parents(options.timepicker_selector).length == 0 && !$target.hasClass('hasTimepicker') && !$target.hasClass('ui-timepicker-trigger')) {
                    self.timepicker.hide();
                }
            }
        });
    },
    
    _toggleTimepicker: function() {
        if (this.timepicker.is(":visible")) {
            this.timepicker.data("current_input", null);
            this.timepicker.hide();
        } else {
            this.timepicker_offset = this.element.offset();
            //this.timepicker_offset.left += this.element.outerWidth() 
            this.timepicker_offset.top += this.element.outerHeight() + this.options.offset.top;
            this.timepicker.css(this.timepicker_offset);
            this.timepicker.data("current_input", this.element);
            this.element.focus();
            this.timepicker.show();
        }
        this.timepicker_open = !this.timepicker_open;
    },
    
    value: function() {
        // calculate some value and return it
        return 25;
    },
    
    length: function() {
        return 22;
    },
    
    destroy: function() {
        $.Widget.prototype.destroy.apply(this, arguments); // default destroy
        // now do other stuff particular to this widget
    }
});

})(jQuery.noConflict());