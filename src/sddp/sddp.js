window.Vue = require('vue');
window.axios = require('axios');
window.axios.defaults.xsrfHeaderName = "X-CSRFToken"
window.axios.defaults.xsrfCookieName = 'csrftoken'

Vue.component('example', require('./components/example.vue').default);
Vue.component('searchComponent', require('./components/search-bar.vue').default);






const app = new Vue({
    el: '#search-app'
});
