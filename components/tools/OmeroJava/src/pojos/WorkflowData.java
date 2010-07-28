/*
* pojos.WorkFlow
*
*------------------------------------------------------------------------------
*  Copyright (C) 2006-2009 University of Dundee. All rights reserved.
*
*
*  This program is free software; you can redistribute it and/or modify
*  it under the terms of the GNU General Public License as published by
*  the Free Software Foundation; either version 2 of the License, or
*  (at your option) any later version.
*  This program is distributed in the hope that it will be useful,
*  but WITHOUT ANY WARRANTY; without even the implied warranty of
*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*  GNU General Public License for more details.
*
*  You should have received a copy of the GNU General Public License along
*  with this program; if not, write to the Free Software Foundation, Inc.,
*  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
*
*------------------------------------------------------------------------------
*/
package pojos;

//Java imports
import java.util.ArrayList;
import java.util.List;

//Third-party libraries

//Application-internal dependencies
import omero.RString;
import omero.model.NamespaceI;

import omero.rtypes;
import pojos.DataObject;

/**
 *
 *
 * @author  Jean-Marie Burel &nbsp;&nbsp;&nbsp;&nbsp;
 * <a href="mailto:j.burel@dundee.ac.uk">j.burel@dundee.ac.uk</a>
 * @author	Donald MacDonald &nbsp;&nbsp;&nbsp;&nbsp;
 * <a href="mailto:donald@lifesci.dundee.ac.uk">donald@lifesci.dundee.ac.uk</a>
 * @version 3.0
 * <small>
 * (<b>Internal version:</b> $Revision: $Date: $)
 * </small>
 * @since 3.0-Beta4
 */
public class WorkflowData
	extends DataObject 
{
	
	/** The default workflow, i.e. nothing .*/
	public static String DEFAULTWORKFLOW = "Default Workflow";
	
	/**
	 * Instantiate the class. 
	 * 
	 * @param workflow The workflow object.
	 */
	public WorkflowData(NamespaceI workflow)
	{
		if (workflow == null) {
            throw new IllegalArgumentException("Object cannot null.");
        }
        setValue(workflow);
	}
	
	/**
	 * Instantiate the class. 
	 * 
	 * @param nameSpace The namespace of the workflow.
	 * @param keywords The keywords of the workflow.
	 */
	public WorkflowData(String nameSpace, List<String> keywords)
	{
		setDirty(true);
		setValue(new NamespaceI());
		
		NamespaceI workflow = (NamespaceI) asIObject();
		if (workflow == null) 
			throw new IllegalArgumentException("No workflow specified.");
   		workflow.setName(rtypes.rstring(nameSpace));
		workflow.setKeywords((String[]) keywords.toArray());
	}
	
	/**
	 * Instantiate the class. 
	 * 
	 * @param nameSpace The namespace of the workflow.
	 * @param keywords The keywords of the workflow.
	 */
	public WorkflowData(String nameSpace, String keywords)
	{
		setDirty(true);
		setValue(new NamespaceI());
		NamespaceI workflow = (NamespaceI) asIObject();
		if (workflow == null) 
			throw new IllegalArgumentException("No workflow specified.");
   		workflow.setName(rtypes.rstring(nameSpace));
		workflow.setKeywords((String[]) CSVToList(keywords).toArray());
	}
	
	/**
	 * Instantiate the class. 
	 * 
	 */
	public WorkflowData()
	{
		setDirty(true);
		setValue(new NamespaceI());
	}
	
	/**
	* Converts a list to a CSV string.
	*
	* @param list The list to convert.
	* @return See above.
	*/
	private String listToCSV(List<String> list)
	{
		String str = "";
		for(int i = 0 ; i < list.size() ; i++)
		{
			str = str + list.get(i);
			if(i<list.size()-1)
				str = str + ",";
		}
		return str;
	}
	
	/**
	* Converts a CSV string to a list of strings.
	*
	* @param str The CSV string to convert.
	* @return See above.
	*/
	private List<String> CSVToList(String str)
	{
		List<String> list = new ArrayList<String>();
		String[] valueString = str.split(",");
		for(String keyword : valueString)
			if(!keyword.equals("[]"))
			{
                System.err.println(keyword);
                list.add(keyword);
            }
		return list;
	}

	/**
	 * Returns the namespace of this workflow.
	 * 
	 * @return See above.
	 */
	public String getNameSpace()
	{
		NamespaceI workflow = (NamespaceI) asIObject();
		if (workflow == null) 
			throw new IllegalArgumentException("No workflow specified.");
  		RString namespace = workflow.getName();
  		if(namespace!=null)
            return namespace.getValue();
        return "";
	}
	
	/**
	 * Returns the keywords of this workflow.
	 * 
	 * @return See above.
	 */
	public String getKeywords()
	{
		NamespaceI workflow = (NamespaceI) asIObject();
		String keywordString = "";
		if (workflow == null) 
			throw new IllegalArgumentException("No workflow specified.");
  		String[] keywords = workflow.getKeywords();
  		for(int i = 0 ; i < keywords.length; i++)
  		{
  			keywordString = keywordString + keywords[i];
  			if(i<keywords.length-1)
  				keywordString = keywordString + ",";
  		}
  		return keywordString;
	}
	
	/**
	 * Returns the keywords of this workflow as a list.
	 * 
	 * @return See above.
	 */
	public List<String> getKeywordsAsList()
	{
		NamespaceI workflow = (NamespaceI) asIObject();
		List<String> keywordList = new ArrayList<String>();
		if (workflow == null) 
			throw new IllegalArgumentException("No workflow specified.");
  		String[] keywords = workflow.getKeywords();
  		if(keywords!=null)
  			for(String keyword : keywords)
  				keywordList.add(keyword);
        return keywordList;
	}
		
	/**
	 * Adds a new keyword to the workflow. 
	 * 
 	 * @param keyword See above.
	 */
	public void addKeyword(String keyword)
	{
		NamespaceI workflow = (NamespaceI) asIObject();
		if (workflow == null) 
			throw new IllegalArgumentException("No workflow specified.");
  		if(contains(keyword))
			throw new IllegalArgumentException("Keyword already exists.");
		List<String> keywords = getKeywordsAsList();
		keywords.add(keyword);
		setKeywords(keywords);
	}
		
	/**
	 * Set the keywords of the workflow. 
	 * 
 	 * @param keywords See above.
	 */
	public void setKeywords(String keywords)
	{
		NamespaceI workflow = (NamespaceI) asIObject();
		if (workflow == null) 
			throw new IllegalArgumentException("No workflow specified.");
		setDirty(true);
		Object keywordObject =  CSVToList(keywords);
		List<String> keywordsList = (List<String>)keywordObject;
		String[] keywordsArray = new String[keywordsList.size()];
		for(int i = 0; i < keywordsList.size(); i++)
			keywordsArray[i]=keywordsList.get(i);
		workflow.setKeywords(keywordsArray);
	}
	
	/**
	 * Set the keywords of the workflow. 
	 * 
 	 * @param keywords See above.
	 */
	public void setKeywords(List<String> keywords)
	{
		NamespaceI workflow = (NamespaceI) asIObject();
		if (workflow == null) 
			throw new IllegalArgumentException("No workflow specified.");
		setDirty(true);
		String[] keywordString = new String[keywords.size()];
		for(int i = 0; i < keywords.size(); i++)
		  keywordString[i] = keywords.get(i);
		workflow.setKeywords(keywordString);
	}
	
	/**
	 * Does the keyword exist in the workflow.
	 * 
	 * @param value keyword to test for existence.
	 * @return See above.
	 */
	public boolean contains(String value)
	{
		NamespaceI workflow = (NamespaceI) asIObject();
		if (workflow == null) 
			throw new IllegalArgumentException("No workflow specified.");
		String[] keywords = workflow.getKeywords();
  		if(keywords==null)
			return false;
		for (String keyword : keywords)
		{
			if (value.equals(keyword))
				return true;
		}
		return false;
	}
	
	/**
	 * Set the namespace of the workflow. 
	 * 
 	 * @param namespace See above.
	 */
	public void setNamespace(String namespace)
	{
		NamespaceI workflow = (NamespaceI) asIObject();
		if (workflow == null) 
			throw new IllegalArgumentException("No workflow specified.");
		setDirty(true);
		workflow.setName(rtypes.rstring(namespace));
	}
	
}
