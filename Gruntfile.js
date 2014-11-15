module.exports = function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),

        sass: {
            dist: {
                options: {
                    style: 'compressed'
                },
                files: {
                    'blender-id/application/static/assets/css/main.css': 'blender-id/application/static/assets/sass/main.sass'
                }
            }
        },

        autoprefixer: {
            no_dest: { src: 'blender-id/application/static/assets/css/main.css' }
        },

        watch: {
            files: ['blender-id/application/static/assets/sass/main.sass'],
            tasks: ['sass', 'autoprefixer'],
        }
    });

    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-autoprefixer');

    grunt.registerTask('default', ['sass', 'autoprefixer']);
};
