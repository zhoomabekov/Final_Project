/**
 * @license Copyright (c) 2003-2023, CKSource Holding sp. z o.o. All rights reserved.
 * For licensing, see https://ckeditor.com/legal/ckeditor-oss-license
 */

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here. For example:
	// config.language = 'fr';
	// config.uiColor = '#AADC6E';
};

CKEDITOR.plugins.addExternal('embed', '/plugins/embed/');

CKEDITOR.replace('my-textarea', {
  extraPlugins: 'embed',
  embed_provider: '//ckeditor.iframe.ly/api/oembed?url={url}&callback={callback}',
});