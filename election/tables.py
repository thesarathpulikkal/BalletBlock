from election.models import Candidate, Position, Elector
import django_tables2 as tables
from django.utils.html import format_html


class CandidateTable(tables.Table):
    #actions = ProductActions(orderable=False) # custom tables.Column()
    id = tables.TemplateColumn('<a href="{% url \'candidate_change\' record.id %}">{{record.id}}</a>')
    delete = tables.TemplateColumn('<a href="{% url \'candidate_delete\' record.id %}"><i class="fas fa-trash-alt"></i></a>')


    class Meta:
        model = Candidate
        fields = ['id', 'name', 'position', 'delete'] # fields to display
        attrs = {'id': 'candidate_table'}
        orderable = False

class PositionTable(tables.Table):
    #actions = ProductActions(orderable=False) # custom tables.Column()
    id = tables.TemplateColumn('<a href="{% url \'position_change\' record.id %}">{{record.id}}</a>')
    delete = tables.TemplateColumn('<a href="{% url \'position_delete\' record.id %}"><i class="fas fa-trash-alt"></i></a>')


    class Meta:
        model = Position
        fields = ['id', 'description', 'quantity', 'delete'] # fields to display
        attrs = {'id': 'position_table'}
        orderable = False

class ElectorTable(tables.Table):
    #actions = ProductActions(orderable=False) # custom tables.Column()
    id = tables.TemplateColumn('<a href="{% url \'elector_change\' record.id %}">{{record.id}}</a>')
    delete = tables.TemplateColumn('<a href="{% url \'elector_delete\' record.id %}"><i class="fas fa-trash-alt"></i></a>')


    class Meta:
        model = Elector
        fields = ['id', 'user.username', 'user.first_name', 'user.last_name', 'user.email', 'delete'] # fields to display
        attrs = {'id': 'elector_table'}
        orderable = False
