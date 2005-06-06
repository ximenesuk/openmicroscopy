/*
 * org.openmicroscopy.shoola.agents.hiviewer.twindow.TinyWindow
 *
 *------------------------------------------------------------------------------
 *
 *  Copyright (C) 2004 Open Microscopy Environment
 *      Massachusetts Institute of Technology,
 *      National Institutes of Health,
 *      University of Dundee
 *
 *
 *
 *    This library is free software; you can redistribute it and/or
 *    modify it under the terms of the GNU Lesser General Public
 *    License as published by the Free Software Foundation; either
 *    version 2.1 of the License, or (at your option) any later version.
 *
 *    This library is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 *    Lesser General Public License for more details.
 *
 *    You should have received a copy of the GNU Lesser General Public
 *    License along with this library; if not, write to the Free Software
 *    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 *------------------------------------------------------------------------------
 */

package org.openmicroscopy.shoola.agents.hiviewer.twindow;


//Java imports
import java.awt.Frame;
import java.awt.Point;
import java.awt.image.BufferedImage;
import javax.swing.JComponent;
import javax.swing.JWindow;

//Third-party libraries

//Application-internal dependencies

/** 
 *  A tiny-looking JWindow.
 * <p>This window has a small title bar and an JComponent to display the 
 * image.
 * <p>The window behaves mostly like a regular window, but has a close and
 * sizing button allowing to collapse/expand the window contents.</p>
 *
 * @author  Jean-Marie Burel &nbsp;&nbsp;&nbsp;&nbsp;
 * 				<a href="mailto:j.burel@dundee.ac.uk">j.burel@dundee.ac.uk</a>
 * @author  <br>Andrea Falconi &nbsp;&nbsp;&nbsp;&nbsp;
 * 				<a href="mailto:a.falconi@dundee.ac.uk">
 * 					a.falconi@dundee.ac.uk</a>
 * @version 2.2
 * <small>
 * (<b>Internal version:</b> $Revision$ $Date$)
 * </small>
 * @since OME2.2
 */
public class TinyWindow
    extends JWindow
{
    
    /** Bound property name indicating if the window is collapsed. */
    public final static String COLLAPSED_PROPERTY = "collapsed";
    
    /** Bound property name indicating if the window is closed. */
    public final static String CLOSED_PROPERTY = "closed";
     
    /** Bound property name indicating if the window's title has changed. */
    public final static String TITLE_PROPERTY = "title";
    
    /** The View component that renders this frame. */
    protected TinyWindowUI    uiDelegate;
    
    /** Tells if this window is expanded or collapsed. */
    private boolean         collapsed;
    
    /** Tells if this window is closed or not. */
    private boolean         closed;
    
    /** The title displayed in this window's title bar. */
    protected String        title;
    
    /**
     * Creates a new window with the specified owner frame.
     * @param owner The frame from which the window is displayed. 
     *              Mustn't be <code>null</code>.
     * @param image The bufferedImage to display. Mustn't be <code>null</code>.
     */
    public TinyWindow(Frame owner, BufferedImage image)
    { 
        this(owner, image, null);
    }
    
    /**
     * Creates a new window with the specified owner frame.
     * 
     * @param owner The frame from which the window is displayed. 
     *              Mustn't be <code>null</code>.
     * @param image The bufferedImage to display. Mustn't be <code>null</code>.
     * @param title The window's title.
     */
    public TinyWindow(Frame owner, BufferedImage image, String title)
    {
        super(owner);
        if (owner == null) throw new NullPointerException("No owner.");
        if (image == null) throw new NullPointerException("No image.");
        this.title = title;
        //Create the View and the Controller.
        uiDelegate = new TinyWindowUI(this, image);
        new WindowControl(this, uiDelegate);
    }
    
    public TinyWindow(Frame owner, JComponent c)
    {
        this(owner, c, null);
    }
    
    public TinyWindow(Frame owner, JComponent c, String title)
    {
        super(owner);
        if (owner == null) throw new NullPointerException("No owner.");
        this.title = title;
        //Create the View and the Controller.
        if (c == null) uiDelegate = new TinyWindowUI(this);
        else uiDelegate = new TinyWindowUI(this, c);
        new WindowControl(this, uiDelegate);
    }
    
    public TinyWindow(Frame owner, String title)
    {
        super(owner);
        this.title = title;
        if (owner == null) throw new NullPointerException("No owner.");
        uiDelegate = new TinyWindowUI(this);
        new WindowControl(this, uiDelegate);
    }
    
    /** Moves the window to the Front. */
    public void moveToFront() { setVisible(true); }
    
    /** 
     * Moves the window to the Front and sets the location
     * 
     * @param x     x-coordinate.
     * @param y     y-coordinate.
     */
    public void moveToFront(int x, int y)
    {
        setLocation(x, y);
        setVisible(true);
    }
    
    /**
     * Moves the window and sets the location.
     * 
     * @param p     New location.
     */
    public void moveToFront(Point p) { moveToFront(p.x, p.y); }
    
    /**
     * Returns the title of the <code>TinyWindow</code>.
     *
     * @return a <code>String</code> containing this window's title
     * @see #setTitle
     */
    public String getTitle() { return title; }
    
    /** 
     * Sets the <code>TinyWindow</code> title. The <code>title</code>
     * may have a <code>null</code> value.
     * @see #getTitle
     *
     * @param title The <code>String</code> to display in the title bar.
     */
    public void setTitle(String title)
    {
        String oldValue = this.title;
        this.title = title;
        firePropertyChange(TITLE_PROPERTY, oldValue, title);
    }
    
    /**
     * Collapses or expands this frame depending on the passed value.
     * This is a bound property; property change listeners are notified
     * of any change to this property. 
     * 
     * @param b Pass <code>true</code> to collapse, <code>false</code> to
     *          expand.
     */
    public void setCollapsed(boolean b)
    {
        if (b == collapsed) return;  //We're already in the requested state.
        //Fire the state change.
        Boolean oldValue = collapsed ? Boolean.TRUE : Boolean.FALSE,
                newValue = b ? Boolean.TRUE : Boolean.FALSE;
        collapsed = b;
        firePropertyChange(COLLAPSED_PROPERTY, oldValue, newValue);
    }
    
    /** 
     * Tells if this frame is expanded or collapsed.
     * 
     * @return <code>true</code> if collapsed, <code>false</code> if expanded. 
     */
    public boolean isCollapsed() { return collapsed; }
    
    /**
     * Closes or opens this window depending on the passed value.
     * This is a bound property; property change listeners are notified
     * of any change to this property. 
     * 
     * @param b Pass <code>true</code> to close, <code>false</code> otherwise.
     */
    public void setClosed(boolean b)
    {
        if (b == closed) return;  //We're already in the requested state.
        //Fire the state change.
        Boolean oldValue = closed ? Boolean.TRUE : Boolean.FALSE,
                newValue = b ? Boolean.TRUE : Boolean.FALSE;
        closed = b;
        firePropertyChange(CLOSED_PROPERTY, oldValue, newValue);
    }
    
    /** 
     * Tells if this window is closed or not.
     * 
     * @return <code>true</code> if closed, <code>false</code> otherwise. 
     */
    public boolean isClosed() { return closed; }
    
    public void closeWindow() { uiDelegate.updateClosedState(); }

}
