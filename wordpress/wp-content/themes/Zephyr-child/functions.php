<?php
/* Custom functions code goes here. */


add_action( 'init', 'mbinfo_register_figure_page' );


function mbinfo_register_figure_page() {
    register_post_type( 'figure', array(
            'labels' => array( 'name' => 'Figures'
            ),
            'rewrite' => array( 'slug' => 'figure', 'with_front' => false ),
            'public' => true, )
    );
}


/**
 * Adds a box to the main column on the Post and Page edit screens.
 */
function mbinfo_figure_meta_box() {

    $screens = array( 'figure' );

    foreach ( $screens as $screen ) {

        add_meta_box(
            'myplugin_sectionid',
            __( 'MBInfo Figure', 'mbinfo_figure_attr_date' ),
            'mbinfo_figure_meta_box_callback',
            $screen
        );
    }
}
add_action( 'add_meta_boxes', 'mbinfo_figure_meta_box' );

/**
 * Prints the box content.
 *
 * @param WP_Post $post The object for the current post/page.
 */
function mbinfo_figure_meta_box_callback( $post ) {

    // Add a nonce field so we can check for it later.
    wp_nonce_field( 'mbinfo_figure_save_meta_box_data', 'mbinfo_figure_meta_box_nonce' );

    /*
     * Use get_post_meta() to retrieve an existing value
     * from the database and use the value for the form.
     */
    $value = get_post_meta( $post->ID, 'mbinfo_figure_attr_date', true );

    echo '<label>' .
        '<input type="text" id="mbinfo_figure_attr_date" name="mbinfo_figure_attr_date"/></label>';
}

/**
 * When the post is saved, saves our custom data.
 *
 * @param int $post_id The ID of the post being saved.
 */
function mbinfo_figure_save_meta_box_data( $post_id ) {

    /*
     * We need to verify this came from our screen and with proper authorization,
     * because the save_post action can be triggered at other times.
     */

    // Check if our nonce is set.
    if ( ! isset( $_POST['mbinfo_figure_meta_box_nonce'] ) ) {
        return;
    }

    // Verify that the nonce is valid.
    if ( ! wp_verify_nonce( $_POST['mbinfo_figure_meta_box_nonce'], 'mbinfo_figure_save_meta_box_data' ) ) {
        return;
    }

    // If this is an autosave, our form has not been submitted, so we don't want to do anything.
    if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) {
        return;
    }

    // Check the user's permissions.
    if ( isset( $_POST['post_type'] ) && 'page' == $_POST['post_type'] ) {

        if ( ! current_user_can( 'edit_page', $post_id ) ) {
            return;
        }

    } else {

        if ( ! current_user_can( 'edit_post', $post_id ) ) {
            return;
        }
    }

    /* OK, it's safe for us to save the data now. */

    // Make sure that it is set.
    if ( ! isset( $_POST['mbinfo_figure_attr_date'] ) ) {
        return;
    }

    // Sanitize user input.
    $my_data = sanitize_text_field( $_POST['mbinfo_figure_attr_date'] );

    // Update the meta field in the database.
    update_post_meta( $post_id, '_my_meta_value_key', $my_data );
}
add_action( 'save_post', 'mbinfo_figure_save_meta_box_data' );
