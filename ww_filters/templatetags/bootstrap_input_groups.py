from django import template
register = template.Library()

from bootstrap3.forms import render_field


@register.simple_tag
def bootstrap_date_field(field, **kwargs):
    calendar_group_wrapper = """
    <div class="bfh-datepicker" data-format="d.m.y">
        <div class="input-group bfh-datepicker-toggle" data-toggle="bfh-datepicker">
            %s<span class="input-group-addon btn"><i class="glyphicon glyphicon-calendar"></i></span>
        </div>
        <div class="bfh-datepicker-calendar">
            <table class="calendar table table-bordered">
                <thead>
                    <tr class="months-header">
                        <th class="month" colspan="4">
                            <a class="previous" href="#"><i class="glyphicon glyphicon-chevron-left"></i></a>
                            <span></span>
                            <a class="next" href="#"><i class="glyphicon glyphicon-chevron-right"></i></a>
                        </th>
                        <th class="year" colspan="3">
                            <a class="previous" href="#"><i class="glyphicon glyphicon-chevron-left"></i></a>
                            <span></span>
                            <a class="next" href="#"><i class="glyphicon glyphicon-chevron-right"></i></a>
                        </th>
                    </tr>
                    <tr class="days-header">
                    </tr>
                </thead>
                <tbody>
                </tbody>
            </table>
        </div>
    </div>
    """
    kwargs['input_wrapper'] = calendar_group_wrapper
    return render_field(field, **kwargs)


@register.simple_tag
def bootstrap_datetime_field(field, **kwargs):
    wrapper = """
    <div class='input-group date' name='bootstrap_datetimepicker'>
        %s<span class="input-group-addon"><span class="glyphicon glyphicon-calendar"></span>
        </span>
    </div>
    """
    kwargs['input_wrapper'] = wrapper
    return render_field(field, **kwargs)
