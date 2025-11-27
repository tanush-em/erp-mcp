# ERP Portal

A modern Enterprise Resource Planning (ERP) dashboard built with Next.js and MongoDB. This portal provides a clean interface to view and manage data from your MongoDB database.

## Features

- 🔍 **Collection Browser**: View all MongoDB collections in your database
- 📊 **Data Visualization**: Clean table display of collection data
- 🎨 **Modern UI**: Beautiful, responsive design with Tailwind CSS
- 🔄 **Real-time Updates**: Refresh data and collections on demand
- 📱 **Mobile Responsive**: Works seamlessly on all devices

## Prerequisites

- Node.js 18+ 
- MongoDB running on `localhost:27017` with database named `erp`

## Getting Started

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Set up Environment Variables** (Optional)
   Create a `.env.local` file in the root directory:
   ```bash
   MONGODB_URI=mongodb://localhost:27017/erp
   ```
   
   If you don't create this file, the app will use the default MongoDB URI.

3. **Start MongoDB**
   Make sure MongoDB is running on your system:
   ```bash
   # Using MongoDB service
   brew services start mongodb-community
   
   # Or start MongoDB directly
   mongod
   ```

4. **Run the Development Server**
   ```bash
   npm run dev
   ```

5. **Open the Application**
   Navigate to [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

1. **View Collections**: The sidebar shows all collections in your MongoDB database
2. **Browse Data**: Click on any collection to view its data in a clean table format
3. **Refresh**: Use the refresh button to reload collections and data
4. **Responsive**: The interface adapts to different screen sizes

## Database Structure

The application will automatically detect and display any collections in your MongoDB database. Common ERP collections might include:

- `employees` - Employee information
- `attendance` - Attendance records
- `leaves` - Leave applications
- `courses` - Training courses
- `departments` - Department information

## API Endpoints

- `GET /api/collections` - Fetch all collections
- `GET /api/data/[collection]` - Fetch data from a specific collection

## Technology Stack

- **Frontend**: Next.js 15, React 19, Tailwind CSS
- **Backend**: Next.js API Routes
- **Database**: MongoDB with Mongoose
- **Icons**: Lucide React

## Future Enhancements

This is a foundation for your ERP system. You can extend it with:
- Analytics and reporting dashboards
- Data entry forms
- User authentication
- Advanced filtering and search
- Export functionality
- Real-time updates

## Contributing

Feel free to submit issues and enhancement requests!

the erp portal looks very poor, the tables shown are just displaying the json. But i want you to understand each data and design the UI accordingly, make a sidebar SHOWING THH EFEATURES IN THE ERP . Ex: for Attendance use the data to be displayed in a monthly calendar like UI. foR TIMETABLES DISPLAY THEM AS GRID LIKE INTERFACE. SO, UBDERSTAND EACH DATA AND DISPLAY THEM ACCORDLINGLY IN A MODERN WAY. DO IT ONW BY ONE, NO ISSUES