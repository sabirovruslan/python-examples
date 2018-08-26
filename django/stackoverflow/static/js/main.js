(function ($) {
    function split(val) {
        return val.split(/,\s*/);
    }

    function extractLast(term) {
        return split(term).pop();
    }

    $('.js-tags').autocomplete({
        source: function (request, response) {
            $.getJSON('/tags', function (data) {
                response($.map(data.tags, function (value) {
                    return {
                        label: value,
                        value: value
                    };
                }));
            });
        },
        search: function () {
            var term = extractLast(this.value);
            if (term.length < 2) {
                return false;
            }
        },
        select: function (event, ui) {
            var terms = split(this.value);
            terms.pop();
            terms.push(ui.item.value);
            terms.push("");
            this.value = terms.join(", ");
            return false;
        }
    });
})(jQuery);
