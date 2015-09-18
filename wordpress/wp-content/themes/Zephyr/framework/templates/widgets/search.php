<?php defined( 'ABSPATH' ) OR die( 'This script cannot be accessed directly.' );

/**
 * Search widget
 *
 * (!) Important: this file is not intended to be overloaded, so use the below hooks for customizing instead
 *
 * @var $layout string Search widget layout: 'simple' / 'popup'
 *
 * @action Before the template: 'us_before_template:templates/widgets/search'
 * @action After the template: 'us_after_template:templates/widgets/search'
 * @filter Template variables: 'us_template_vars:templates/widgets/search'
 */

$layout = isset( $layout ) ? $layout : 'simple';

$form_template_vars = array(
	'type' => 'search',
	'action' => home_url( '/' ),
	'method' => 'get',
	'fields' => array(
		's' => array(
			'type' => 'textfield',
			'title' => ( $layout == 'popup' ) ? __( 'Just type and press \'enter\'', 'us' ) : '',
			'placeholder' => ( $layout == 'simple' ) ? ( __( 'search', 'us' ) . ' ...' ) : '',
		),
		'submit' => array(
			'type' => 'submit',
			'title' => __( 'Search', 'us' ),
		),
	),
);
if ( $layout == 'popup' ) {
	$form_template_vars['end_html'] = '<div class="w-search-close"></div>';
}
if ( defined( 'ICL_LANGUAGE_CODE' ) AND ICL_LANGUAGE_CODE != '' ) {
	$form_template_vars['fields']['lang'] = array(
		'type' => 'hidden',
		'name' => 'lang',
		'value' => ICL_LANGUAGE_CODE,
	);
}
?>
<div class="w-search layout_<?php echo $layout ?>">

	<?php if ( $layout == 'popup' ): ?>
		<div class="w-search-open"></div>
		<div class="w-search-background"></div>
	<?php endif; ?>

	<?php us_load_template( 'templates/form/form', $form_template_vars ) ?>
</div>
