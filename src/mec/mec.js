window.Vue = require('vue');
window.axios = require('axios');
window._ = require('lodash');

Vue.component('example', require('./components/example.vue').default);

Vue.component('searchComponent', require('./components/search-bar.vue').default);


window.axios.defaults.xsrfCookieName = 'csrftoken';
window.axios.defaults.xsrfHeaderName = 'X-CSRFToken';




const app = new Vue({
    el: '#search-app'
});


