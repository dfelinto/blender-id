var gulp          = require('gulp'),
    plumber       = require('gulp-plumber'),
    sass          = require('gulp-sass'),
    sourcemaps    = require('gulp-sourcemaps'),
    autoprefixer  = require('gulp-autoprefixer'),
    jade          = require('gulp-jade'),
    livereload    = require('gulp-livereload');


/* CSS */
gulp.task('styles', function() {
    gulp.src('blender-id/src/styles/**/*.sass')
        .pipe(plumber())
        .pipe(sourcemaps.init())
        .pipe(sass({
            outputStyle: 'compressed'}
            ))
        .pipe(autoprefixer("last 3 version", "safari 5", "ie 8", "ie 9"))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest('blender-id/application/static/assets/css'))
        .pipe(livereload());
});


/* Templates - Jade */
gulp.task('templates', function() {
    gulp.src('blender-id/src/templates/**/*.jade')
        .pipe(plumber())
        .pipe(jade({
            pretty: true
        }))
        .pipe(gulp.dest('blender-id/application/templates/'))
        .pipe(livereload());
});


// While developing, run 'gulp watch'
gulp.task('watch',function() {
    livereload.listen();

    gulp.watch('blender-id/src/styles/**/*.sass',['styles']);
    gulp.watch('blender-id/src/templates/**/*.jade',['templates']);
});


// Run 'gulp' to build everything at once
gulp.task('default', ['styles', 'templates']);
