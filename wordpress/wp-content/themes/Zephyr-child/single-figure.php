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
    <div class="l-titlebar-h i-cf"><h1>Contractile Fiber</h1>


    </div>
</div>

<div class="l-main">
    <div class="l-main-h i-cf">

        <div class="l-content g-html">
            <?php do_action( 'us_before_single' ) ?>
            <section class="l-section">
            <?php
            require_once WP_PLUGIN_DIR . '/mbinfo-figure/mbinfo.php';
            $mbinfo = new Mbinfo();
            echo $mbinfo->render_figure_copyright([], '');
            ?>
            </section>
            <?php do_action( 'us_after_single' ) ?>
        </div>
    </div>
</div>

<?php get_footer(); ?>

