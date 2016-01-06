<?php
/**
 * Template Name: Topic Home
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
            the_post();

            do_action('us_before_single');
            ?>
            <section class="l-section">
                <div class="l-section-h i-cf">
                    <p><br/><br/></p>

                    <div class="g-cols offset_medium">

                        <div class=" one-quarter">
                            <div class="wpb_text_column ">
                                <div class="wpb_wrapper">
                                    <div class="w-image "><a href="/topics/cellular-organization/">
                                            <img
                                                src="/wp-content/uploads/2015/04/MBInfo-Web-sub-Icons_cyto_dynam_teal.png"
                                                width="500" height="500" alt=""></a>
                                    </div>
                                    <div class="wpb_text_column ">
                                        <div class="wpb_wrapper" style="text-align: center">
                                            <p>
                                            </p>
                                            <h6>Cellular Organization</h6>

                                            <p></p>

                                            <p>
                                                <a href="/topics/cellular-organization/">Explore &gt;</a>
                                            </p>

                                            <p></p>
                                        </div>
                                    </div>


                                </div>
                            </div>
                        </div>
                        <div class=" one-quarter">
                            <div class="wpb_text_column ">
                                <div class="wpb_wrapper">
                                    <div class="w-image "><a href="/topics/cytoskeleton-dynamics/"><img
                                                src="/wp-content/uploads/2015/04/MBInfo-Web-sub-Icons_cell_org_teal1.png"
                                                width="500" height="500" alt=""></a></div>
                                    <div class="wpb_text_column ">
                                        <div class="wpb_wrapper" style="text-align: center">
                                            <p>
                                            </p>
                                            <h6>Cytoskeleton Dynamics</h6>

                                            <p></p>

                                            <p>
                                                <a href="/topics/cytoskeleton-dynamics/">Explore &gt;</a>
                                            </p>

                                            <p></p>
                                        </div>
                                    </div>


                                </div>
                            </div>
                        </div>
                        <div class=" one-quarter">
                            <div class="wpb_text_column ">
                                <div class="wpb_wrapper">
                                    <div class="w-image "><a href="/topics/mechanosignaling/"><img
                                                src="/wp-content/uploads/2015/05/MBInfo-Web-sub-Icons_Mechano_Signal_teal.png"
                                                width="500" height="500" alt=""></a></div>
                                    <div class="wpb_text_column ">
                                        <div class="wpb_wrapper" style="text-align: center">
                                            <p>
                                            </p>
                                            <h6>Mechanosignaling</h6>

                                            <p></p>

                                            <p>
                                                <a href="/topics/mechanosignaling/">Explore &gt;</a>
                                            </p>

                                            <p></p>
                                        </div>
                                    </div>


                                </div>
                            </div>
                        </div>
                        <div class=" one-quarter">
                            <div class="wpb_text_column ">
                                <div class="wpb_wrapper">
                                    <div class="w-image "><a href="/topics/synthesis/"><img
                                                src="/wp-content/uploads/2015/04/MBInfo-Web-sub-Icons_Synthesis_teal.png"
                                                width="500" height="500" alt=""></a></div>
                                    <div class="wpb_text_column ">
                                        <div class="wpb_wrapper" style="text-align: center">
                                            <p>
                                            </p>
                                            <h6>Synthesis</h6>

                                            <p></p>

                                            <p>
                                                <a href="/topics/synthesis/">Explore &gt;</a>
                                            </p>

                                            <p></p>
                                        </div>
                                    </div>


                                </div>
                            </div>
                        </div>
                    </div>
                    <p><br/><br/></p>

                    <?php

                    $the_content = apply_filters('the_content', get_the_content());
                    echo $the_content;
                    do_action('us_after_single');

                    ?>
                </div>
            </section>
        </div>
    </div>
</div>


<?php get_footer(); ?>

