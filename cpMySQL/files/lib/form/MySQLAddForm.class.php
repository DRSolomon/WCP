<?php
require_once (CP_DIR . 'lib/data/ftp/FTPUserEditor.class.php');
require_once (WCF_DIR . 'lib/form/AbstractSecureForm.class.php');

class FTPAddForm extends AbstractSecureForm
{
	/**
	 * @see AbstractPage::$templateName
	 */
	public $templateName = 'mysqlAdd';

	public $password = '';

	public $description = '';

	public $mysql;

	/**
	 * @see Form::readFormParameters()
	 */
	public function readFormParameters()
	{
		parent :: readFormParameters();

		if (isset($_POST['password']))
			$this->password = StringUtil :: trim($_POST['password']);

		if (isset($_POST['description']))
			$this->description = StringUtil :: trim($_POST['description']);
	}

	/**
	 * @see Form::validate()
	 */
	public function validate()
	{
		parent :: validate();

		if (empty($this->password))
			throw new UserInputException('password', 'notempty');

		if (WCF :: getUser()->mysqls <= WCF :: getUser()->mysqlsUsed)
			throw new UserInputException('mysql', 'tomuch');
	}

	/**
	 * @see Page::assignVariables()
	 */
	public function assignVariables()
	{
		parent :: assignVariables();

		WCF :: getTPL()->assign(array (
			'password' => $this->password,
			'description' => $this->description,
		));
	}

	/**
	 * @see Form::save()
	 */
	public function save()
	{
		parent :: save();

		// create
		$this->mysql = MySQLEditor :: create(WCF :: getUser()->userID,
											 WCF :: getUser()->username,
											 $this->password,
											 $this->description
											);
		$this->saved();

		$url = 'index.php?page=MySQLList'. SID_ARG_2ND_NOT_ENCODED;
		HeaderUtil::redirect($url);
	}

	/**
	 * @see Page::show()
	 */
	public function show()
	{
		require_once(WCF_DIR.'lib/page/util/menu/PageMenu.class.php');
		PageMenu::setActiveMenuItem('cp.header.menu.mysql');

		if (WCF :: getUser()->mysqls <= WCF :: getUser()->mysqlsUsed)
		{
			require_once(WCF_DIR.'lib/system/exception/PermissionDeniedException.class.php');
			throw new PermissionDeniedException();
		}

		parent :: show();
	}
}
?>