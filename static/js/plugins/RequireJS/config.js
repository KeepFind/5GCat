require.config({
    baseUrl: '/static/js/plugins/RequireJS',
    paths: {
//            'jquery': '../framework/jquery-1.11.3.min', 
//         'bootstrap': '../framework/bootstrap.min', 
//            'jquery': '../framework/jquery-1.8.min', 
        'bootstrap': '../../bootstrap.min',
        'map': 'http://api.map.baidu.com/getscript?v=2.0&ak=F51571495f717ff1194de02366bb8da9&services=&t=20140530104353',
    },
    shim: {
        'bootstrap': {
            exports: "$",
            // deps: ['jquery']
        },
        'map': {
            exports: 'BMap'
        }
    }
});