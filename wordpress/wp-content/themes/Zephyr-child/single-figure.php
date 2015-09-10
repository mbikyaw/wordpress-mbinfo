<?php
/**
 * Created by PhpStorm.
 * User: mbikyaw
 * Date: 3/9/15
 * Time: 11:06 AM
 */
get_header();
?>

<div class="l-titlebar size_medium color_alternate">
    <div class="l-titlebar-h i-cf">
        <?php the_title('<h1>', '</h1>') ?>
    </div>
</div>

<div class="l-main">
    <div class="l-main-h i-cf">

        <div class="l-content g-html">
            <?php
            require_once WP_PLUGIN_DIR . '/mbinfo-figure/includes/mbinfo.php';

            do_action( 'us_before_single' );
            echo '<section class="l-section">';

            global $post;
            if (current_user_can('edit_pages')) {
                $js_fn = plugins_url('/mbinfo-figure/js/uploader.js');
                echo '<div id="uploader-root"></div>';
                echo '<script src="https://apis.google.com/js/client.js"></script>';
                echo '<script src="' . $js_fn . '""></script>';
            }
            $date = get_post_meta( $post->ID, Mbinfo::$ATTR_DATE, true );
            $attr = [
                'id' => $post->post_name,
                'title' => $post->post_title,
                'created' => $date
            ];

            $mbinfo = new Mbinfo();
            echo $mbinfo->render_figure_copyright($attr, $post->post_content);

            echo '</section>';
            do_action( 'us_after_single' );
            ?>
        </div>
    </div>
</div>

<?php get_footer(); ?>

