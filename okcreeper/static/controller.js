angular.module('creep', []).
  config(['$routeProvider', function($routeProvider) {
  $routeProvider.
      when('/:username', {templateUrl: 'static/creep_template.html', controller: CreepCtrl}).
      otherwise({redirectTo: ''});
}]);

function CreepCtrl($scope, $routeParams, $http, $anchorScroll) {

    $scope.loading = true
    $scope.username = $routeParams.username;

    $http.get('creep/' + $routeParams.username + '.json')
        .success(function(data) {
            $scope.loading = false;
            $scope.response = data;
            console.log(data);
            setTimeout(function(){$('body').scrollTo('#un')});
        }).error(function(data, status, headers, config) {
            $scope.loading = false;
            $scope.error = true;
    });

    $scope.question_page_marker = 0;
    $scope.questions = [];
    $scope.more_questions = true;
    $scope.get_questions_message = 'get questions'

    $scope.getquestions = function() {
        $scope.loading = true;
        $scope.more_questions = false;
        $http.get('questions/' + $routeParams.username + '/' + $scope.question_page_marker + '.json')
            .success(function(data) {
                if('total_questions' in data){
                    $scope.total_questions = data['total_questions'];
                }
                $scope.questions.push.apply($scope.questions, data['questions']);
                $scope.loading = false;
                $scope.question_page_marker += 3;
                $scope.get_questions_message = 'get more questions';
                $scope.more_questions = data['more'];
            }).error(function(data, status, headers, config) {
                $scope.loading = false;
                $scope.error = true;
        });
 
    }

}

// scrollTo taken from http://lions-mark.com/jquery/scrollTo/
$.fn.scrollTo = function( target, options, callback ){
  if(typeof options == 'function' && arguments.length == 2){ callback = options; options = target; }
  var settings = $.extend({
    scrollTarget  : target,
    offsetTop     : 50,
    duration      : 500,
    easing        : 'swing'
  }, options);
  return this.each(function(){
    var scrollPane = $(this);
    var scrollTarget = (typeof settings.scrollTarget == "number") ? settings.scrollTarget : $(settings.scrollTarget);
    var scrollY = (typeof scrollTarget == "number") ? scrollTarget : scrollTarget.offset().top + scrollPane.scrollTop() - parseInt(settings.offsetTop);
    scrollPane.animate({scrollTop : scrollY }, parseInt(settings.duration), settings.easing, function(){
      if (typeof callback == 'function') { callback.call(this); }
    });
  });
}

$(document).ready(function() {
    $(window).scroll(function(){
        if($(window).scrollTop() == 0){$('#jump').fadeOut();}
        else{$('#jump').fadeIn();}
    });
    $("#jump").bind("click", function(){window.scrollTo(0,0)});
});