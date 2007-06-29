/*
 * org.openmicroscopy.shoola.agents.measurement.view.ROIAssistantModel 
 *
  *------------------------------------------------------------------------------
 *  Copyright (C) 2006-2007 University of Dundee. All rights reserved.
 *
 *
 * 	This program is free software; you can redistribute it and/or modify
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
package org.openmicroscopy.shoola.agents.measurement.view;

//Java imports
import java.util.ArrayList;
import java.util.Iterator;
import java.util.TreeMap;

import javax.swing.table.AbstractTableModel;


//Third-party libraries

//Application-internal dependencies
import org.openmicroscopy.shoola.util.roi.exception.NoSuchROIException;
import org.openmicroscopy.shoola.util.roi.model.ROI;
import org.openmicroscopy.shoola.util.roi.model.ROIShape;
import org.openmicroscopy.shoola.util.roi.model.util.Coord3D;

/** 
 * 
 *
 * @author  Jean-Marie Burel &nbsp;&nbsp;&nbsp;&nbsp;
 * 	<a href="mailto:j.burel@dundee.ac.uk">j.burel@dundee.ac.uk</a>
 * @author	Donald MacDonald &nbsp;&nbsp;&nbsp;&nbsp;
 * 	<a href="mailto:donald@lifesci.dundee.ac.uk">donald@lifesci.dundee.ac.uk</a>
 * @version 3.0
 * <small>
 * (<b>Internal version:</b> $Revision: $Date: $)
 * </small>
 * @since OME3.0
 */
public class ROIAssistantModel
	extends AbstractTableModel
{	
	/** The roi this table model is based on. */
	private ROI							currentROI;
	
	/** The current plane of the viewer. */
	private Coord3D 					currentPlane;
	
	/** The number of columns in the model. */
	private int							numColumns;
	
	/** The number of the rows in the model. */
	private int 						numRows;
	
	private TreeMap<Coord3D, String> 	shapeMap;
	
	private ArrayList<String> 			columnNames;
	
	/**
	 * Model of the ROIAssistant to store the current locations of the ROIs
	 * on the images, and their type.
	 * @param numRow The number of z sections in the image. 
	 * @param numCol The numer of time points in the image. 
	 * @param currentPlane the current plane of the image.
	 * @param roi The ROI which will be propagated.
	 */
	ROIAssistantModel(int numCol, int numRow, Coord3D currentPlane, ROI roi)
	{
		this.setColumnCount(numCol+1);
		this.setRowCount(numRow);
		this.columnNames = new ArrayList<String>();
		this.currentPlane = currentPlane;
		currentROI = roi;
		columnNames.add("Z Section\\Time");
		shapeMap = new TreeMap<Coord3D, String>(new Coord3D());
		for(int i = 0 ; i < numCol ; i++)
			columnNames.add((i+1)+"");
		populateShapeMap();
	}

	/**
	 * Populate the shape Map of the model with all the ROIShapes of the 
	 * current ROI. 
	 *
	 */
	private void populateShapeMap()
	{
		shapeMap.clear();
		TreeMap<Coord3D, ROIShape> list = currentROI.getShapes();
		Iterator<ROIShape> shapeIterator = list.values().iterator();
		while(shapeIterator.hasNext())
		{
			ROIShape shape = shapeIterator.next();
			Coord3D coord = shape.getCoord3D();
			numRows = Math.max(numRows, coord.getZSection());
			String type = shape.getFigure().getType();
			shapeMap.put(coord, type);
		}
	}
	
	/* (non-Javadoc)
	 * @see javax.swing.table.TableModel#getColumnCount()
	 */
	public int getColumnCount()
	{
		return numColumns;
	}

	/**
	 * Overridden to return the name of the specified column.
	 * @see AbstractTableModel#getColumnName(int)
	 */
	public String getColumnName(int col) { return columnNames.get(col); }

	/* (non-Javadoc)
	 * @see javax.swing.table.TableModel#getRowCount()
	 */
	public int getRowCount()
	{
		return numRows;
	}

	/** 
	 * Set the value of the model to the object.
	 */
	public void setValueAt(Object value, int col, int row)
	{
		
	}
	
	/**
	 * Get the shape at zSection, timePoint which refers to the column and
	 * row in the model.
	 * @param zSection the row of the table.
	 * @param timePoint the col of the model.
	 * @return see above.
	 */
	public ROIShape getShapeAt(int zSection, int timePoint)
	{
		try
		{
			int translateZ = (getRowCount()-zSection);
			ROIShape shape = currentROI.getShape(new Coord3D(timePoint-1, translateZ-1));
			if(shape == null)
			{
				return null;
			}
			return shape;
		}
		catch (NoSuchROIException e)
		{
			return null;
		}
	}
	
	/* (non-Javadoc)
	 * @see javax.swing.table.TableModel#getValueAt(int, int)
	 */
	public Object getValueAt(int zSection, int timePoint)
	{
		int translateZ = (getRowCount()-zSection);
		if(timePoint == 0)
		{
			return translateZ+"";
		}
		try
		{
			ROIShape shape = currentROI.getShape(new Coord3D(timePoint-1, translateZ-1));
			if(shape == null)
			{
				return null;
			}
			return shape.getFigure().getType();
		}
		catch (NoSuchROIException e)
		{
			return null;
		}
	}
	
	/**
	 * Set the number of columns in the table to col.
	 * @param col see above.
	 */
	public void setColumnCount(int col)
	{
		numColumns = col;
	}
	
	/**
	 * Set the number of rows in the table to col.
	 * @param row see above.
	 */
	public void setRowCount(int row)
	{
		numRows = row;
	}
	
}


