(function($) {
	"use strict";
	$.fn.acknowledgeinput = function(options) {
		var acknowledgeVars = {
			success_color : "#468847",
			danger_color : "#bd362f",
			icon_success : "icon-ok fa fa-check",
			icon_danger : "icon-warning-sign fa fa-warning",
			update_on : "change",
			default_state : "visible",
			override_val : true,
			bootstrap_version : 0
		}, addOnClass, updateIcons;
		updateIcons = function(inputEl) {
			var re, data_type, required, pattern, isEmail, isTel, isNumber, isInt, isDecimal, isCurrency, isColour, isUrl, modify_classes, isNotNullOrEmpty;
			modify_classes = function modify_classes(isSuccess, iconClass) {
				var colour = isSuccess ? acknowledgeVars.success_color
						: acknowledgeVars.danger_color;
				inputEl.parent().find("[data-role=acknowledgement]").css(
						"color", colour).find("i").removeClass().addClass(
						iconClass)
			};
			isNotNullOrEmpty = function isNotNullOrEmpty(value) {
				return value !== null && value !== undefined
						&& value.trim() !== ""
			};
			inputEl.parent().find("[data-role=acknowledgement]").addClass(
					addOnClass).find("i").removeClass();
			data_type = inputEl.data("type") === undefined ? "text" : inputEl
					.data("type");
			data_type = data_type.toLowerCase();
			required = inputEl.attr("required") === undefined ? false : inputEl
					.attr("required").toLowerCase() === "required";
			pattern = inputEl.data("pattern") === undefined ? "" : inputEl
					.data("pattern");
			if (data_type === "text") {
				if (isNotNullOrEmpty(inputEl.val())) {
					modify_classes(true, acknowledgeVars.icon_success)
				} else if (required) {
					modify_classes(false, acknowledgeVars.icon_danger)
				}
			} else if (data_type === "email") {
				re = /^(([^<>()\[\]\\.,;:\s@\"]+(\.[^<>()\[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
				isEmail = re.test(inputEl.val());
				if (isNotNullOrEmpty(inputEl.val()) && isEmail) {
					modify_classes(true, acknowledgeVars.icon_success)
				} else if (required || isNotNullOrEmpty(inputEl.val())
						&& !isEmail) {
					modify_classes(false, acknowledgeVars.icon_danger)
				}
			} else if (data_type === "tel") {
				re = /^(\+)?( |-|\(|\)|[0-9]){4,50}$/;
				isTel = re.test(inputEl.val());
				if (isNotNullOrEmpty(inputEl.val()) && isTel) {
					modify_classes(true, acknowledgeVars.icon_success)
				} else if (required || isNotNullOrEmpty(inputEl.val())
						&& !isTel) {
					modify_classes(false, acknowledgeVars.icon_danger)
				}
			} else if (data_type === "number") {
				re = /^(\-)?([0-9])+$/;
				isNumber = re.test(inputEl.val());
				if (isNotNullOrEmpty(inputEl.val()) && isNumber) {
					modify_classes(true, acknowledgeVars.icon_success)
				} else if (required || isNotNullOrEmpty(inputEl.val())
						&& !isNumber) {
					modify_classes(false, acknowledgeVars.icon_danger)
				}
			} else if (data_type === "integer") {
				re = /^(\-)?(([1-9])([0-9])+|0)$/;
				isInt = re.test(inputEl.val());
				if (isNotNullOrEmpty(inputEl.val()) && isInt) {
					modify_classes(true, acknowledgeVars.icon_success)
				} else if (required || isNotNullOrEmpty(inputEl.val())
						&& !isInt) {
					modify_classes(false, acknowledgeVars.icon_danger)
				}
			} else if (data_type === "decimal") {
				re = /^(\-)?(([0-9])+(\.)([0-9])+|0)$/;
				isDecimal = re.test(inputEl.val());
				if (isNotNullOrEmpty(inputEl.val()) && isDecimal) {
					modify_classes(true, acknowledgeVars.icon_success)
				} else if (required || isNotNullOrEmpty(inputEl.val())
						&& !isDecimal) {
					modify_classes(false, acknowledgeVars.icon_danger)
				}
			} else if (data_type === "currency") {
				re = /^(([0-9])+((\.|,)?([0-9]){2,2})?)$/;
				isCurrency = re.test(inputEl.val());
				if (isNotNullOrEmpty(inputEl.val()) && isCurrency) {
					modify_classes(true, acknowledgeVars.icon_success)
				} else if (required || isNotNullOrEmpty(inputEl.val())
						&& !isCurrency) {
					modify_classes(false, acknowledgeVars.icon_danger)
				}
			} else if (data_type === "colour" || data_type === "color") {
				isColour = $("<span></span>").css({
					color : "transparent"
				}).css({
					color : inputEl.val()
				}).css("color") !== "transparent";
				if (isNotNullOrEmpty(inputEl.val()) && isColour) {
					modify_classes(true, acknowledgeVars.icon_success)
				} else if (required || isNotNullOrEmpty(inputEl.val())
						&& !isColour) {
					modify_classes(false, acknowledgeVars.icon_danger)
				}
			} else if (data_type === "url") {
				re = /^(https?:\/\/)?([\da-z\.\-]+)\.([a-z\.]{2,6})([\/\w \.\-]*)*\/?$/;
				isUrl = re.test(inputEl.val());
				if (isNotNullOrEmpty(inputEl.val()) && isUrl) {
					modify_classes(true, acknowledgeVars.icon_success)
				} else if (required || isNotNullOrEmpty(inputEl.val())
						&& !isUrl) {
					modify_classes(false, acknowledgeVars.icon_danger)
				}
			} else if (data_type === "custom") {
				re = new RegExp(pattern, "i");
				isUrl = re.test(inputEl.val());
				if (isNotNullOrEmpty(inputEl.val()) && isUrl) {
					modify_classes(true, acknowledgeVars.icon_success)
				} else if (required || isNotNullOrEmpty(inputEl.val())
						&& !isUrl) {
					modify_classes(false, acknowledgeVars.icon_danger)
				}
			}
		};
		$.extend(acknowledgeVars, options);
		if (acknowledgeVars.bootstrap_version === 2) {
			addOnClass = "add-on"
		} else if (acknowledgeVars.bootstrap_version === 3) {
			addOnClass = "input-group-addon"
		} else {
			addOnClass = "input-group-addon add-on"
		}
		$("[data-role=acknowledge-input]").find(
				"input:not([type=radio]):not([type=checkbox]),textarea,select")
				.each(
						function() {
							updateIcons($(this));
							if (acknowledgeVars.default_state !== "visible") {
								$(this).parent().find(
										"[data-role=acknowledgement]")
										.addClass(addOnClass).find("i")
										.removeClass()
							}
						}).on(acknowledgeVars.update_on, function() {
					updateIcons($(this))
				});
		if (acknowledgeVars.override_val) {
			(function($) {
				var originalVal = $.fn.val;
				$.fn.val = function(value) {
					if (value !== undefined) {
						if (this.parent().data("role") === "acknowledge-input") {
							return originalVal.call(this, value).change()
						}
					}
					return originalVal.apply(this, arguments)
				}
			})(jQuery)
		}
	}
})(window.jQuery);